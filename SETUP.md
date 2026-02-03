# SQL Genie - Setup Complete! 🎉

## ✅ What's Ready
- Backend with FastAPI + WebSocket streaming
- MCP Database Bridge for PostgreSQL
- LLM integration (OpenAI & Anthropic support)
- React frontend with real-time chat
- Sample database with customers and orders

## 🔑 Next Steps

### 1. Add your LLM API Key
Edit `.env` file and uncomment one of these:

**For OpenAI:**
```bash
OPENAI_API_KEY=sk-...
```
Get your key: https://platform.openai.com/api-keys

**For Anthropic:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```
Get your key: https://console.anthropic.com/

### 2. Restart the backend
The backend auto-reloads, but to pick up .env changes:
- Close the backend terminal
- Run: `.\start.ps1`

### 3. Try it out!
Ask questions like:
- "Who are the top 5 customers by total spend?"
- "Show me all pending orders"
- "How many customers are from the USA?"
- "What's the average order value by country?"

## 📊 Sample Data
The database now has:
- **customers** table: 10 customers from different countries
- **orders** table: 14 orders with various amounts and statuses

## 🎯 Test Queries
```sql
-- Top customers by spend
SELECT customer_name, SUM(total_amount) as total_revenue 
FROM customers c JOIN orders o ON c.customer_id = o.customer_id 
GROUP BY customer_name ORDER BY total_revenue DESC LIMIT 5;

-- Pending orders
SELECT * FROM orders WHERE status = 'pending';

-- Orders by country
SELECT country, COUNT(*) as order_count, SUM(total_amount) as total
FROM customers c JOIN orders o ON c.customer_id = o.customer_id
GROUP BY country ORDER BY total DESC;
```

## 🛠️ Troubleshooting
- Backend not running? Check terminal for errors
- Frontend disconnected? Ensure backend is on port 8000
- No LLM response? Verify API key in .env and restart backend
- Database errors? Run: `docker compose up -d db`

## 📁 Project Structure
```
backend/
  app/
    main.py          # FastAPI app + WebSocket
    agent.py         # Reasoning agent with LLM
    llm_service.py   # OpenAI/Anthropic integration
    mcp_server.py    # Database bridge
    config.py        # Settings
frontend/
  src/
    App.jsx          # Chat interface
```

Enjoy exploring your database with natural language! 🚀
