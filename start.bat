@echo off
REM Start SQL Genie: Backend + Frontend

echo 🧞 Starting SQL Genie...

REM Start backend in new window
echo ▶ Starting Backend (FastAPI)...
start "SQL Genie Backend" cmd /k "cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000"

REM Wait for backend to initialize
timeout /t 2 /nobreak >nul

REM Start frontend in new window
echo ▶ Starting Frontend (Vite)...
start "SQL Genie Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ✅ Both services starting in separate windows!
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
