@echo off
echo Starting Streamlit Frontend for FastAPI Backend...
echo.
echo Make sure the FastAPI backend is running first!
echo Start it with: start_fastapi.bat
echo.
echo This will open your browser to http://localhost:8501
echo Press Ctrl+C to stop the Streamlit app
echo.
echo | python -m streamlit run main_streamlit_app_fastapi.py --server.port 8501 --server.headless true
