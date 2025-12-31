@echo off
echo ================================================
echo   INICIANDO BACKEND V63 (REPARADO)
echo ================================================
echo.
echo Deteniendo procesos Python anteriores...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo Iniciando Backend V63 en puerto 8001...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v63"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
