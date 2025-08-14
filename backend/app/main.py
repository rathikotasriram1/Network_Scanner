import os, asyncio, json
from fastapi import FastAPI, WebSocket, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .nessus import NessusClient
from .db import init_db, save_scan_meta, set_status, finalize_scan, get_scans_list, get_scan_details
from .realtime import manager

app = FastAPI(title="AI Cyber Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

init_db()
nessus = NessusClient()

class StartScanReq(BaseModel):
    target: str
    template_uuid: str
    name: str = "Nessus Scan"

@app.post("/scan/start")
async def start_scan(req: StartScanReq, bg: BackgroundTasks):
    nes_id = await nessus.create_scan(req.name, req.target, req.template_uuid)
    await nessus.launch_scan(nes_id)
    db_id = await save_scan_meta(source="nessus", target=req.target, raw_ref=str(nes_id))
    bg.add_task(track_scan_until_done, nes_id, db_id)
    return {"ok": True, "scan_db_id": db_id}

async def track_scan_until_done(nes_id: int, db_id: int):
    while True:
        status, raw = await nessus.get_scan_status(nes_id)
        await set_status(db_id, status)
        await manager.broadcast({"scan_db_id": db_id, "status": status})
        if status.lower() == "completed":
            break
        await asyncio.sleep(3)
    results = await nessus.export_results_json(nes_id)
    # very small summary: severity buckets
    counts = {"info":0,"low":0,"medium":0,"high":0,"critical":0}
    for v in results.get("vulnerabilities", []):
        sev = (v.get("severity") or "").lower()
        if sev in counts: counts[sev] += v.get("count", 0) if isinstance(v.get("count"), int) else 1
    await finalize_scan(db_id, {"severity_counts": counts})
    await manager.broadcast({"scan_db_id": db_id, "status": "completed", "counts": counts})

@app.get("/scans")
async def scans():
    return await get_scans_list()

@app.get("/scans/{scan_id}")
async def scan_details(scan_id: int):
    return await get_scan_details(scan_id) or {"error":"not found"}

# Debug endpoint to help verify UUIDs and scanners
@app.get("/nessus/debug")
async def nessus_debug():
    templates = await nessus.get_templates()
    scanners  = await nessus.get_scanners()
    # return a trimmed view
    tmpl = [
        {"name": t.get("name"), "title": t.get("title"), "uuid": t.get("uuid")}
        for t in templates.get("templates", [])
    ]
    scn = [
        {"id": s.get("id"), "name": s.get("name"), "type": s.get("type")}
        for s in scanners.get("scanners", [])
    ]
    return {"templates": tmpl, "scanners": scn}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive (ignored)
    except Exception:
        pass
    finally:
        manager.disconnect(ws)
