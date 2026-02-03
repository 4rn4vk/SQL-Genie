from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def build_engine(database_url: str) -> Engine:
    """Create a synchronous SQLAlchemy engine."""

    return create_engine(database_url, future=True, pool_pre_ping=True)


def run_select(engine: Engine, query: str) -> list[dict]:
    """Execute a read-only SELECT query and return rows as dictionaries."""

    normalized = query.strip().lower()
    if not normalized.startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")

    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = [dict(row._mapping) for row in result]
    return rows
