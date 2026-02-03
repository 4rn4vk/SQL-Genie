from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating SQL from natural language using LLMs."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.client = None
        
        if self.provider == "openai":
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not configured. LLM features disabled.")
                return
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        elif self.provider == "anthropic":
            if not settings.anthropic_api_key:
                logger.warning("Anthropic API key not configured. LLM features disabled.")
                return
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
        else:
            logger.warning(f"Unknown LLM provider: {self.provider}. LLM features disabled.")

    def is_available(self) -> bool:
        """Check if LLM service is configured and available."""
        return self.client is not None

    def _build_system_prompt(self, schema: dict) -> str:
        """Build a system prompt with database schema context."""
        tables_info = []
        for table_name, columns in schema.get("tables", {}).items():
            cols = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            tables_info.append(f"- {table_name}: {cols}")
        
        tables_str = "\n".join(tables_info) if tables_info else "No tables available"
        
        return f"""You are an expert SQL assistant for a {schema.get('dialect', 'SQL')} database.

Database Schema:
{tables_str}

Your task:
1. Translate the user's natural language question into a valid SQL SELECT query
2. Only generate SELECT statements - no INSERT, UPDATE, DELETE, or DROP
3. Return ONLY the SQL query without any explanation or markdown formatting
4. Use proper {schema.get('dialect', 'SQL')} syntax
5. If the question cannot be answered with available tables, explain why briefly

Example:
User: "Show me the top 5 customers by revenue"
Assistant: SELECT customer_name, SUM(revenue) as total_revenue FROM customers GROUP BY customer_name ORDER BY total_revenue DESC LIMIT 5
"""

    async def generate_sql_streaming(
        self, user_question: str, schema: dict
    ) -> AsyncGenerator[str, None]:
        """Generate SQL from natural language with streaming response."""
        if not self.is_available():
            yield "⚠️ LLM not configured. Please add your API key to .env file.\n"
            yield "Set OPENAI_API_KEY or ANTHROPIC_API_KEY and restart the backend."
            return

        system_prompt = self._build_system_prompt(schema)
        
        try:
            if self.provider == "openai":
                async for token in self._stream_openai(user_question, system_prompt):
                    yield token
            elif self.provider == "anthropic":
                async for token in self._stream_anthropic(user_question, system_prompt):
                    yield token
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            yield f"\n\n❌ Error generating SQL: {str(e)}"

    async def _stream_openai(
        self, user_question: str, system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            stream=True,
            temperature=0.1,
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _stream_anthropic(
        self, user_question: str, system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """Stream response from Anthropic."""
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_question}],
            temperature=0.1,
        ) as stream:
            async for text in stream.text_stream:
                yield text
