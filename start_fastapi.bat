@echo off
echo Starting FastAPI Database Query Assistant Backend...
echo.
echo This will start the FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo API Endpoints will be available at:
echo   - http://localhost:8000/docs (Interactive API documentation)
echo   - http://localhost:8000/query (POST - Submit queries)
echo   - http://localhost:8000/health (GET - Health check)
echo   - http://localhost:8000/tables (GET - List tables)
echo.
uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload
