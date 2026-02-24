from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Walk up from backend/app/ to find the nearest .env file (supports running
# uvicorn from backend/ or the project root).
_here = Path(__file__).parent
_env_file = next(
    (str(p) for p in [_here / ".env", _here.parent / ".env", _here.parent.parent / ".env"] if p.exists()),
    ".env",
)


class Settings(BaseSettings):
    """Application configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=_env_file, env_file_encoding="utf-8", extra="ignore")

    # Supported schemes:
    #   SQLite:     sqlite:///./sql_genie.db          (default — no setup needed)
    #   DuckDB:     duckdb:///./sql_genie.duckdb
    #   PostgreSQL: postgresql://user:pass@host/db
    database_url: str = "sqlite:///./sql_genie.db"
    mcp_schema_resource: str = "db_schema"
    # Dialect is auto-detected from database_url when left blank.
    mcp_dialect: str = ""

    # LLM Configuration
    llm_provider: str = "openai"  # "openai" or "anthropic"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    allowed_origins: list[str] = ["http://localhost:5173"]

    @model_validator(mode="after")
    def _auto_detect_dialect(self) -> "Settings":
        """Infer mcp_dialect from database_url if not explicitly set."""
        if not self.mcp_dialect:
            url = self.database_url.lower()
            if url.startswith("postgresql") or url.startswith("postgres"):
                self.mcp_dialect = "postgresql"
            elif url.startswith("duckdb"):
                self.mcp_dialect = "duckdb"
            elif url.startswith("sqlite"):
                self.mcp_dialect = "sqlite"
            else:
                self.mcp_dialect = "sql"
        return self


settings = Settings()
