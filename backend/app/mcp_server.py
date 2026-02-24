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
        """Inspect the database and return a simple schema map.

        Uses native catalog queries for DuckDB and SQLite to avoid SQLAlchemy
        firing pg_catalog introspection SQL that those dialects don't support.
        """
        tables: dict[str, list[dict]] = {}

        if self.dialect == "duckdb":
            tables = self._schema_duckdb()
        elif self.dialect == "sqlite":
            tables = self._schema_sqlite()
        else:
            # PostgreSQL and others — SQLAlchemy inspector works fine.
            inspector = inspect(self.engine)
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                tables[table_name] = [
                    {"name": col["name"], "type": str(col["type"])} for col in columns
                ]

        return {"dialect": self.dialect, "tables": tables}

    # ------------------------------------------------------------------
    # Dialect-specific schema helpers
    # ------------------------------------------------------------------

    def _schema_duckdb(self) -> dict[str, list[dict]]:
        """Return schema map by querying DuckDB's information_schema directly."""
        tables: dict[str, list[dict]] = {}
        with self.engine.connect() as conn:
            # List tables in the default (main) schema
            rows = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'main' ORDER BY table_name"
                )
            ).fetchall()
            for (table_name,) in rows:
                cols = conn.execute(
                    text(
                        "SELECT column_name, data_type "
                        "FROM information_schema.columns "
                        "WHERE table_schema = 'main' AND table_name = :t "
                        "ORDER BY ordinal_position"
                    ),
                    {"t": table_name},
                ).fetchall()
                tables[table_name] = [
                    {"name": col_name, "type": data_type}
                    for col_name, data_type in cols
                ]
        return tables

    def _schema_sqlite(self) -> dict[str, list[dict]]:
        """Return schema map by querying SQLite's sqlite_master and PRAGMA."""
        tables: dict[str, list[dict]] = {}
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            ).fetchall()
            for (table_name,) in rows:
                cols = conn.execute(
                    text(f"PRAGMA table_info({table_name})")  # noqa: S608
                ).fetchall()
                # PRAGMA columns: cid, name, type, notnull, dflt_value, pk
                tables[table_name] = [
                    {"name": col[1], "type": col[2]} for col in cols
                ]
        return tables

    def execute_read_query(self, query: str) -> list[dict]:
        """Execute a read-only SELECT query and return rows as dictionaries."""
        normalized = query.strip().lower()
        if not normalized.startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")

        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            rows = [dict(row._mapping) for row in result]
        return rows
