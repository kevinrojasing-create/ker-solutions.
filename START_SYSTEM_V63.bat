@echo off
echo ========================================================
echo   INICIO COMPLETO - SISTEMA KER V63
echo ========================================================
echo.

REM Detener procesos anteriores
echo Deteniendo procesos anteriores...
taskkill /F /FI "WINDOWTITLE eq Backend*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Flutter*" 2>nul
timeout /t 2 >nul

echo.
echo [1/2] Iniciando Backend V63 (Python 3.11)...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v63"
start "Backend V63" cmd /k START_V63_PY311.bat

echo.
echo Esperando 8 segundos para que el backend inicie...
timeout /t 8

echo.
echo [2/2] Iniciando App Flutter...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_app"
start "Flutter App" cmd /k "set PATH=%PATH%;C:\Users\kevin\flutter\bin && flutter run -d chrome"

echo.
echo ========================================================
echo   SISTEMA COMPLETO INICIADO
echo ========================================================
echo.
echo Backend V63: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo App Flutter: Se abrira en Chrome
echo.
echo Presiona cualquier tecla para cerrar...
pause
