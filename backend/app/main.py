from __future__ import annotations

import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.agent import ReasoningAgent
from app.config import settings
from app.mcp_server import MCPDatabaseBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SQL Genie", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bridge = MCPDatabaseBridge(settings.database_url, settings.mcp_dialect)
agent = ReasoningAgent(bridge)


@app.on_event("startup")
async def startup_event():
    """Log startup configuration details."""
    logger.info("🧞 SQL Genie backend starting...")
    logger.info(f"   Database: {settings.database_url}")
    logger.info(f"   CORS origins: {settings.allowed_origins}")
    logger.info("   WebSocket endpoint: ws://localhost:8000/ws/chat")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint for uptime monitoring."""
    return {"status": "ok"}


@app.get("/schema")
async def schema() -> dict:
    """Expose the database schema for the UI/agent."""
    return bridge.get_schema_map()


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket) -> None:
    """Handle a streaming chat session over WebSocket."""
    await websocket.accept()
    try:
        while True:
            # Receive a user message, stream tokens back, then mark end of response
            user_message = await websocket.receive_text()
            async for token in agent.astream_chat(user_message):
                await websocket.send_text(token)
            await websocket.send_text("[[END_OF_MESSAGE]]")
    except WebSocketDisconnect:
        return
    except Exception as exc:  # pragma: no cover - runtime guard
        await websocket.send_text(f"Error: {exc}")
        await websocket.send_text("[[END_OF_MESSAGE]]")
