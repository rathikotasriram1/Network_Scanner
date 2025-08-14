from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text
from datetime import datetime

class Base(DeclarativeBase): pass

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(32), default="nessus")
    target: Mapped[str] = mapped_column(String(512))
    raw_ref: Mapped[str] = mapped_column(String(64))  # Nessus scan id as string
    status: Mapped[str] = mapped_column(String(32), default="created")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
