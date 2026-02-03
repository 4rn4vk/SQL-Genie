# SQL Genie

Agentic database assistant: FastAPI backend with an MCP-style bridge to PostgreSQL, LangChain-ready reasoning loop, and a React chat UI that streams responses over WebSockets.

## Quick start (Local Development)
**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Windows (Batch):**
```cmd
start.bat
```

Both scripts will open separate windows for backend and frontend services.

## Quick start (Docker)
1) Copy `.env.example` to `.env` and adjust secrets.
2) `docker compose up --build`
3) Backend: http://localhost:8000/docs, WebSocket: ws://localhost:8000/ws/chat
4) Connect your frontend dev server to ws://localhost:8000/ws/chat (proxy already set in vite config).

## Dev setup (backend)
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Dev setup (frontend)
```bash
cd frontend
npm install
npm run dev -- --host --port 5173
```

## Testing
```bash
cd backend
pytest
```

## Architecture highlights
- FastAPI app exposes `/schema`, `/health`, and `/ws/chat` for streaming agent replies.
- MCP bridge: schema discovery via SQLAlchemy inspector; read-only execution guard on SELECT statements.
- Agent stub streams incremental text; swap in a LangChain chain to generate SQL and call the bridge.
- React + Vite UI with WebSocket streaming and minimal styling; room to add Chart.js rendering when numeric series are returned.

## Environment
- `DATABASE_URL` should point at your Postgres instance (docker-compose provides one at `postgresql://postgres:postgres@db:5432/sql_genie`).
- `OPENAI_API_KEY` optional placeholder; wire into the agent when adding a real LLM.
- `ALLOWED_ORIGINS` comma-separated origins for CORS.
