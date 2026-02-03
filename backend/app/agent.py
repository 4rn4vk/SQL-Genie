from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncGenerator

from app.llm_service import LLMService
from app.mcp_server import MCPDatabaseBridge


class ReasoningAgent:
    """Agent that translates natural language to SQL and executes queries."""

    def __init__(self, bridge: MCPDatabaseBridge) -> None:
        self.bridge = bridge
        self.llm_service = LLMService()

    async def astream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Process user message and stream response."""
        yield f"🤔 Analyzing: '{message}'\n\n"
        await asyncio.sleep(0.1)
        
        try:
            # Get database schema
            schema = self.bridge.get_schema_map()
            tables = ", ".join(schema.get("tables", {}).keys()) or "(no tables)"
            
            yield f"📊 Database: {schema.get('dialect', 'unknown')}\n"
            yield f"📋 Tables: {tables}\n\n"
            await asyncio.sleep(0.1)
            
            if not self.llm_service.is_available():
                yield "⚠️ LLM not configured. Please add your API key to .env:\n"
                yield "1. Copy .env.example to .env\n"
                yield "2. Add OPENAI_API_KEY=sk-... or ANTHROPIC_API_KEY=sk-ant-...\n"
                yield "3. Restart the backend\n"
                return
            
            # Generate SQL using LLM
            yield "🔮 Generating SQL query...\n\n"
            sql_query = ""
            async for token in self.llm_service.generate_sql_streaming(message, schema):
                sql_query += token
                yield token
            
            sql_query = sql_query.strip()
            
            # Check if it's a valid SELECT query
            if not sql_query.lower().startswith("select"):
                yield "\n\n⚠️ Not a SELECT query - execution skipped for safety."
                return
            
            # Execute the query
            yield "\n\n⚡ Executing query...\n"
            await asyncio.sleep(0.2)
            
            try:
                results = self.bridge.execute_read_query(sql_query)
                
                if not results:
                    yield "📭 No results found.\n"
                    return
                
                # Format results
                yield f"\n✅ Found {len(results)} row(s):\n\n"
                
                # Show all results in a readable format
                for i, row in enumerate(results, 1):
                    formatted_row = {}
                    for k, v in row.items():
                        # Format datetime objects nicely
                        if hasattr(v, 'isoformat'):
                            formatted_row[k] = v.isoformat()
                        else:
                            formatted_row[k] = v
                    yield f"{i}. {str(formatted_row)}\n"
                    
            except Exception as e:
                yield f"\n❌ Query execution failed: {str(e)}\n"
                
        except Exception as e:
            yield f"\n❌ Error: {str(e)}"
