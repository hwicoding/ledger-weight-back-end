@echo off
chcp 65001 >nul
echo ========================================
echo Ledger Weight Backend Server Start
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Virtual environment not found. Please create it first.
    echo python -m venv venv
    pause
    exit /b 1
)

echo.
echo Starting server...
echo Press Ctrl+C to stop
echo.
echo Access URLs:
echo   - HTTP: http://localhost:8080
echo   - WebSocket: ws://localhost:8080
echo   - API Docs: http://localhost:8080/docs
echo.

REM 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

pause

