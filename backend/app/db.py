from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool, StaticPool


def build_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine with dialect-appropriate pool settings.

    - SQLite:     StaticPool + check_same_thread=False (safe for FastAPI threads)
    - DuckDB:     NullPool (DuckDB allows only one writer; pooling causes conflicts)
    - PostgreSQL: default pool with pool_pre_ping for connection health checks
    """
    url_lower = database_url.lower()

    if url_lower.startswith("sqlite"):
        return create_engine(
            database_url,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    if url_lower.startswith("duckdb"):
        # duckdb-engine handles the dialect; NullPool avoids concurrent-writer errors.
        return create_engine(database_url, future=True, poolclass=NullPool)

    # PostgreSQL (and any other dialect) — standard pooling
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
