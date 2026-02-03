from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.db import build_engine


class MCPDatabaseBridge:
    """Lightweight MCP-like bridge exposing schema and a read-only query tool."""

    def __init__(self, database_url: str, dialect: str = "postgresql") -> None:
        self.database_url = database_url
        self.dialect = dialect
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """Lazy engine initialization - only connects when first accessed."""
        if self._engine is None:
            self._engine = build_engine(self.database_url)
        return self._engine

    def get_schema_map(self) -> dict:
        inspector = inspect(self.engine)
        tables: dict[str, list[dict]] = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            tables[table_name] = [
                {"name": col["name"], "type": str(col["type"])} for col in columns
            ]
        return {"dialect": self.dialect, "tables": tables}

    def execute_read_query(self, query: str) -> list[dict]:
        normalized = query.strip().lower()
        if not normalized.startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")

        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            rows = [dict(row._mapping) for row in result]
        return rows
