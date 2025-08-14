# backend/app/nessus.py
import os, asyncio, httpx

class NessusClient:
    def __init__(self, base=None):
        self.base = base or os.getenv("NESSUS_BASE", "https://localhost:8834")
        self.headers = {
            "X-ApiKeys": f"accessKey={os.getenv('NESSUS_ACCESS')}; secretKey={os.getenv('NESSUS_SECRET')}",
            "Content-Type": "application/json"
        }
        self.verify = os.getenv("NESSUS_VERIFY_TLS", "false").lower() == "true"

    async def _client(self):
        return httpx.AsyncClient(verify=self.verify, timeout=120)

    async def get_templates(self):
        async with await self._client() as c:
            r = await c.get(f"{self.base}/editor/scan/templates", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def get_scanners(self):
        async with await self._client() as c:
            r = await c.get(f"{self.base}/scanners", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def create_scan(self, name: str, target: str, template_uuid: str) -> int:
        # try to pick a local scanner id if available
        scanners = await self.get_scanners()
        scanner_id = None
        # Prefer a local nessus scanner
        for s in scanners.get("scanners", []):
            if s.get("type") in ("nessus", "local") or s.get("name", "").lower().startswith("nessus"):
                scanner_id = s.get("id"); break
        # Fallback: first scanner if any
        if scanner_id is None and scanners.get("scanners"):
            scanner_id = scanners["scanners"][0].get("id")

        payload = {
            "uuid": template_uuid,
            "settings": {
                "name": name,
                "text_targets": target
            }
        }
        if scanner_id is not None:
            payload["settings"]["scanner_id"] = scanner_id

        async with await self._client() as c:
            r = await c.post(f"{self.base}/scans", headers=self.headers, json=payload)
            if r.status_code >= 400:
                # Surface Nessus error body to logs for quick debugging
                try:
                    detail = r.json()
                except Exception:
                    detail = {"text": r.text}
                raise httpx.HTTPStatusError(f"{r.status_code} creating scan: {detail}", request=r.request, response=r)
            return r.json()["scan"]["id"]

    async def launch_scan(self, scan_id: int):
        async with await self._client() as c:
            r = await c.post(f"{self.base}/scans/{scan_id}/launch", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def get_scan_status(self, scan_id: int):
        async with await self._client() as c:
            r = await c.get(f"{self.base}/scans/{scan_id}", headers=self.headers)
            r.raise_for_status()
            j = r.json()
            return j["info"]["status"], j

    async def export_results_json(self, scan_id: int):
        async with await self._client() as c:
            r = await c.post(f"{self.base}/scans/{scan_id}/export", headers=self.headers, json={"format": "json"})
            r.raise_for_status()
            file_id = r.json()["file"]
            # poll
            while True:
                s = await c.get(f"{self.base}/scans/{scan_id}/export/{file_id}/status", headers=self.headers)
                s.raise_for_status()
                if s.json().get("status") == "ready":
                    break
                await asyncio.sleep(2)
            d = await c.get(f"{self.base}/scans/{scan_id}/export/{file_id}/download", headers=self.headers)
            d.raise_for_status()
            return d.json()
