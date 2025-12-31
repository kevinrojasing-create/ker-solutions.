@echo off
echo ================================================
echo   LIMPIEZA Y LANZAMIENTO V62
echo ================================================

echo Deteniendo procesos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM dart.exe 2>nul
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 >nul

echo.
echo Iniciando Backend V62 (Puerto 8000)...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v62"
start "Backend V62" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo.
echo Esperando backend...
timeout /t 5

echo.
echo Iniciando Flutter App...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_app"
start "Flutter App" cmd /k "set PATH=%PATH%;C:\Users\kevin\flutter\bin && flutter run -d chrome"

echo.
echo LISTO!
pause
