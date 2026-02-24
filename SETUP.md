# SQL Genie - Setup Guide

## What's Ready
- Backend: FastAPI + WebSocket streaming
- MCP Database Bridge with dialect-aware support for **DuckDB, SQLite, and PostgreSQL**
- LLM integration (OpenAI & Anthropic)
- React frontend with real-time chat
- Sample data scripts for all three databases

---

## Step 1 — Choose a Database

Edit `.env` and set `DATABASE_URL` to one of the following:

```dotenv
# DuckDB (default — best for local analytics)
DATABASE_URL=duckdb:///./sql_genie.duckdb

# SQLite (zero-install, great for demos)
DATABASE_URL=sqlite:///./sql_genie.db

# PostgreSQL (production / multi-user)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

The dialect is auto-detected — no other changes needed.

---

## Step 2 — Seed Sample Data

**DuckDB:**
```powershell
cd backend
python seed_duckdb.py
```

**SQLite:**
```powershell
python -c "import sqlite3, pathlib; conn=sqlite3.connect('sql_genie.db'); conn.executescript(pathlib.Path('../sample_data_sqlite.sql').read_text()); conn.close(); print('Done')"
```

**PostgreSQL:**
```powershell
docker compose --profile postgres up -d db
# wait a few seconds, then:
psql postgresql://postgres:postgres@localhost:5432/sql_genie -f sample_data.sql
```

You can also skip seeding entirely and point `DATABASE_URL` at any existing database file or server.

---

## Step 3 — Add Your LLM Key

In `.env`, set one of:

```dotenv
# Anthropic (Claude)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Get keys at: https://console.anthropic.com/ or https://platform.openai.com/api-keys

---

## Step 4 — Start the App

```powershell
# Backend (from /backend)
uvicorn app.main:app --reload

# Frontend (from /frontend, separate terminal)
npm install
npm run dev
```

Or use the convenience scripts from the project root:
```powershell
.\start.ps1    # PowerShell
start.bat      # CMD
```

Frontend: http://localhost:5173  
API docs: http://localhost:8000/docs

---

## Sample Queries to Try

- "Who are the top 5 customers by total spend?"
- "Show me all pending orders"
- "How many customers are from the USA?"
- "What's the average order value by country?"

```sql
-- Top customers
SELECT c.customer_name, SUM(o.total_amount) AS total_revenue
FROM customers c JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name ORDER BY total_revenue DESC LIMIT 5;

-- Pending orders
SELECT * FROM orders WHERE status = 'pending';

-- Revenue by country
SELECT c.country, COUNT(*) AS order_count, SUM(o.total_amount) AS total
FROM customers c JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.country ORDER BY total DESC;
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `(no tables)` in response | Re-run the seed script for your chosen DB |
| `TryCast` import error | `pip install "sqlalchemy>=2.0.30"` |
| `pg_collation` error | You're using DuckDB — this is fixed in `mcp_server.py` automatically |
| Anthropic key warning | Check for a leading space in `ANTHROPIC_API_KEY=` in `.env` |
| Backend not picking up `.env` | Ensure `.env` is in the `backend/` folder (or the project root — both are searched) |
| DuckDB write-lock error | Close any other tool (DBeaver, CLI) that has the `.duckdb` file open with write access |
| Database errors with Docker Postgres | Run: `docker compose --profile postgres up -d db` |
