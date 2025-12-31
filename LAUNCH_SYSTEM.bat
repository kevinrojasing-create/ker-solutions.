@echo off
echo ===================================================
echo   KER SOLUTIONS V63 - LAUNCHER MAESTRO
echo ===================================================
echo.
echo Iniciando Backend V63...
echo (Asegurate de haber cerrado cualquier otra ventana negra antes)
start "KER BACKEND V63" cmd /k "cd backend_v63 && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Esperando 8 segundos para que el backend inicie...
timeout /t 8 /nobreak > nul

echo.
echo Iniciando Frontend Flutter...
cd ker_app
call START_APP.bat
