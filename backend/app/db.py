import os, json, asyncio
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from .models import Base, Scan
from datetime import datetime

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./cyber.sqlite")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(engine)

async def save_scan_meta(source: str, target: str, raw_ref: str) -> int:
    s = Scan(source=source, target=target, raw_ref=raw_ref, status="launched")
    with SessionLocal() as sess:
        sess.add(s)
        sess.commit()
        sess.refresh(s)
        return s.id

async def set_status(scan_db_id: int, status: str):
    with SessionLocal() as sess:
        sess.execute(update(Scan).where(Scan.id == scan_db_id).values(status=status))
        sess.commit()

async def finalize_scan(scan_db_id: int, summary: dict):
    with SessionLocal() as sess:
        sess.execute(update(Scan).where(Scan.id == scan_db_id).values(
            status="completed", finished_at=datetime.utcnow(), summary_json=json.dumps(summary)
        ))
        sess.commit()

async def get_scans_list():
    with SessionLocal() as sess:
        rows = sess.execute(select(Scan).order_by(Scan.id.desc())).scalars().all()
        return [dict(id=r.id, source=r.source, target=r.target, raw_ref=r.raw_ref, status=r.status,
                    started_at=r.started_at.isoformat(),
                    finished_at=(r.finished_at.isoformat() if r.finished_at else None),
                    summary_json=r.summary_json) for r in rows]

async def get_scan_details(scan_id: int):
    with SessionLocal() as sess:
        r = sess.get(Scan, scan_id)
        if not r: return None
        return dict(id=r.id, source=r.source, target=r.target, raw_ref=r.raw_ref, status=r.status,
                    started_at=r.started_at.isoformat(),
                    finished_at=(r.finished_at.isoformat() if r.finished_at else None),
                    summary_json=r.summary_json)
