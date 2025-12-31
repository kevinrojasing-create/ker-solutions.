@echo off
echo ========================================
echo V62 Server Startup (NO VENV)
echo ========================================

REM Kill all Python processes
taskkill /F /IM python.exe /T 2>nul

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start server WITHOUT venv
echo Starting server...
C:\Users\kevin\AppData\Local\Microsoft\WindowsApps\python.exe -m uvicorn main:app --reload

pause
