@echo off
echo ================================================
echo   INICIANDO SISTEMA COMPLETO - BACKEND V62
echo ================================================
echo.
echo Cerrando procesos anteriores...
taskkill /F /FI "WINDOWTITLE eq Backend*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Flutter*" 2>nul
timeout /t 2 >nul

echo.
echo [1/2] Iniciando Backend V62 en puerto 8000...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v62"
start "Backend V62" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [2/2] Esperando 5 segundos para que backend inicie...
timeout /t 5

echo.
echo Iniciando App Flutter en Chrome...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_app"

echo Actualizando configuracion...
powershell -Command "(Get-Content 'lib\config\app_config.dart') -replace 'localhost:8001', 'localhost:8000' | Set-Content 'lib\config\app_config.dart'"
powershell -Command "(Get-Content 'lib\services\api.dart') -replace 'localhost:8001', 'localhost:8000' | Set-Content 'lib\services\api.dart'"

echo.
start "Flutter App" cmd /k "set PATH=%PATH%;C:\Users\kevin\flutter\bin && flutter run -d chrome"

echo.
echo ================================================
echo  SISTEMA INICIADO CORRECTAMENTE
echo ================================================
echo.
echo Backend V62: http://localhost:8000
echo App Flutter: Se abrira automaticamente en Chrome
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause
