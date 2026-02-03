#!/usr/bin/env pwsh
# Start SQL Genie: Backend + Frontend

Write-Host "🧞 Starting SQL Genie..." -ForegroundColor Cyan

# Start backend in new window
Write-Host "▶ Starting Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload --port 8000"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 2

# Start frontend in new window
Write-Host "▶ Starting Frontend (Vite)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev"

Write-Host "`n✅ Both services starting in separate windows!" -ForegroundColor Cyan
Write-Host "   Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
