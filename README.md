# SQL Genie

Agentic database assistant: FastAPI backend with an MCP-style bridge to **DuckDB, SQLite, or PostgreSQL**, LangChain-ready reasoning loop, and a React chat UI that streams responses over WebSockets.

---

## Supported Databases

| Database | Connection string | Best for |
|---|---|---|
| **DuckDB** *(default)* | `duckdb:///./sql_genie.duckdb` | Local analytics, large file queries, Parquet/CSV |
| **SQLite** | `sqlite:///./sql_genie.db` | Lightweight local use, zero-config |
| **PostgreSQL** | `postgresql://user:pass@host/db` | Production, multi-user, cloud deployments |

Switch databases by changing one line in `.env` — the dialect is auto-detected and no other code changes are needed.

---

## Quick Start (Local — DuckDB, no Docker needed)

```powershell
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Create .env (DuckDB is the default)
copy ..\.env.example ..\.env
# Add your LLM key to .env:
# ANTHROPIC_API_KEY=sk-ant-...  or  OPENAI_API_KEY=sk-...

# 3. Seed the DuckDB database with sample data
python seed_duckdb.py

# 4. Start the backend
uvicorn app.main:app --reload

# 5. In a second terminal, start the frontend
cd ..frontend
npm install
npm run dev
```

Frontend: http://localhost:5173  
Backend API docs: http://localhost:8000/docs

---

## Quick Start (Windows scripts)

```powershell
.\start.ps1      # PowerShell
start.bat        # CMD
```

Both scripts open separate windows for backend and frontend.

---

## Quick Start (Docker)

**SQLite or DuckDB** (no extra services needed):
```powershell
docker compose up --build
```

**PostgreSQL** (activates the `db` container):
```powershell
docker compose --profile postgres up --build
```

Set `DATABASE_URL` in `docker-compose.yml` accordingly (three pre-commented options are provided).

---

## Database Integration Details

### DuckDB

DuckDB is a file-based analytical database — no server process required.

**How it works in SQL Genie:**
- `db.py` creates the engine with `NullPool` to avoid DuckDB's single-writer lock.
- `mcp_server.py` uses `information_schema.tables` / `information_schema.columns` for schema discovery instead of SQLAlchemy's default `pg_catalog` introspection (which DuckDB does not support).
- All queries are read-only `SELECT` statements enforced at the bridge layer.

**Connecting an existing DuckDB file:**
```dotenv
# .env
DATABASE_URL=duckdb:///C:/path/to/your_database.duckdb
```

**Seeding sample data:**
```powershell
cd backend
python seed_duckdb.py
```

**External tools** that can create/populate the `.duckdb` file before pointing SQL Genie at it:
- DuckDB UI: `duckdb your_database.duckdb -ui`
- DuckDB CLI: `duckdb your_database.duckdb`
- DBeaver (add a DuckDB driver, open the file)
- Harlequin TUI: `pip install harlequin && harlequin your_database.duckdb`

> **Note:** DuckDB allows multiple concurrent readers but only one writer at a time. SQL Genie is read-only so it coexists safely with open GUI tools, but avoid holding a write connection in another tool while the backend is running.

**Scalability with DuckDB:**
- DuckDB is vectorised and columnar — it handles hundreds of millions of rows on a single machine comfortably.
- You can attach Parquet files, CSV files, or even S3 buckets directly as virtual tables without importing data:
  ```sql
  SELECT * FROM read_parquet('s3://bucket/data/*.parquet') LIMIT 100;
  SELECT * FROM read_csv_auto('C:/data/sales.csv');
  ```
- For multi-user or write-heavy workloads, migrate to PostgreSQL by swapping the `DATABASE_URL`.

---

### SQLite

SQLite is built into Python — no installation needed.

**How it works in SQL Genie:**
- `db.py` creates the engine with `StaticPool` and `check_same_thread=False` for safe use inside FastAPI's async threads.
- `mcp_server.py` uses `sqlite_master` and `PRAGMA table_info()` for schema discovery.

**Connecting:**
```dotenv
# .env
DATABASE_URL=sqlite:///./sql_genie.db
```

**Seeding sample data:**
```powershell
sqlite3 backend/sql_genie.db ".read sample_data_sqlite.sql"
# or via Python:
python -c "import sqlite3, pathlib; conn=sqlite3.connect('backend/sql_genie.db'); conn.executescript(pathlib.Path('sample_data_sqlite.sql').read_text()); conn.close()"
```

**Scalability with SQLite:**
- Suitable for development, demos, and single-user tools. Handles databases up to several GB reliably.
- Read concurrency is fine; writes are serialised. SQL Genie is read-only so concurrent queries work without issue.
- For larger datasets or team use, export to DuckDB (which can read SQLite files directly) or migrate to PostgreSQL.

---

### PostgreSQL

**How it works in SQL Genie:**
- `db.py` uses standard pooling with `pool_pre_ping` for connection health checks.
- `mcp_server.py` falls through to SQLAlchemy's full inspector which uses `pg_catalog` — the most complete introspection available.

**Connecting:**
```dotenv
# .env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**Scalability with PostgreSQL:**
- Production-grade: supports concurrent users, row-level security, partitioning, and full ACID compliance.
- Works with managed cloud services: AWS RDS, Supabase, Neon, Railway, etc. — just change `DATABASE_URL`.

---

## Architecture

```
User message (natural language)
        │
        ▼
   React UI  ──WebSocket──►  FastAPI /ws/chat
                                    │
                              ReasoningAgent
                              ┌─────┴──────┐
                         LLMService    MCPDatabaseBridge
                      (OpenAI/Claude)   │
                                   ┌───┴────────┐
                               Schema map   execute_read_query
                               (dialect-    (SELECT only)
                                native)
                                    │
                              SQLAlchemy Engine
                              ┌─────┼──────┐
                           DuckDB SQLite  PostgreSQL
```

- **`config.py`** — reads `.env`, auto-detects dialect from `DATABASE_URL`.
- **`db.py`** — builds the engine with dialect-appropriate pool settings.
- **`mcp_server.py`** — dialect-aware schema discovery; enforces read-only SELECT guard.
- **`agent.py`** — streams step-by-step reasoning, calls LLM for SQL generation, executes and formats results.
- **`llm_service.py`** — OpenAI and Anthropic streaming support.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `duckdb:///./sql_genie.db` | Database connection string |
| `LLM_PROVIDER` | `openai` | `openai` or `anthropic` |
| `OPENAI_API_KEY` | — | OpenAI key (if using OpenAI) |
| `ANTHROPIC_API_KEY` | — | Anthropic key (if using Claude) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Anthropic model name |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins (comma-separated) |

---

## Testing

```bash
cd backend
pytest
```

---

## Project Structure

```
backend/
  app/
    main.py          # FastAPI app + WebSocket endpoint
    agent.py         # Reasoning agent — LLM + SQL execution loop
    llm_service.py   # OpenAI / Anthropic streaming
    mcp_server.py    # Database bridge — dialect-aware schema + query
    db.py            # SQLAlchemy engine factory (DuckDB / SQLite / Postgres)
    config.py        # Pydantic settings with dialect auto-detection
  seed_duckdb.py     # One-time DuckDB sample data seeder
  requirements.txt
frontend/
  src/
    App.jsx          # Chat UI with WebSocket streaming
sample_data.sql          # PostgreSQL seed
sample_data_sqlite.sql   # SQLite seed
sample_data_duckdb.sql   # DuckDB seed
docker-compose.yml       # Postgres behind --profile postgres; SQLite/DuckDB default
```
