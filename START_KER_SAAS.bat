@echo off
echo ================================================
echo   INICIANDO KER SAAS (CORREGIDO)
echo ================================================
echo.

echo [1/2] Iniciando Backend (Port 8000)...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_saas\backend"
echo Iniciando Uvicorn...
start /min "Backend SaaS" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo [2/2] Iniciando Frontend (Port 5000)...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_saas\frontend\ker_app"
echo Ejecutando Flutter en Chrome...
"C:\Users\kevin\flutter\bin\flutter.bat" run -d chrome --web-port=5000
