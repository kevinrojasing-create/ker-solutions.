@echo off
echo ========================================================
echo   INICIANDO BACKEND V63 CON PYTHON 3.11
echo ========================================================
echo.

cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v63"

if not exist venv_311 (
    echo ERROR: Entorno virtual no encontrado.
    echo Ejecuta primero: SETUP_PYTHON311.bat
    pause
    exit /b 1
)

echo Activando entorno virtual Python 3.11...
call venv_311\Scripts\activate.bat

echo.
echo Iniciando Backend V63 en puerto 8001...
echo Backend URL: http://localhost:8001
echo Documentacion: http://localhost:8001/docs
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
