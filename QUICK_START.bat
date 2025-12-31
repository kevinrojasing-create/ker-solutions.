@echo off
echo ============================================
echo  SOLUCION RAPIDA - INICIANDO SISTEMA
echo ============================================
echo.
echo Este script va a:
echo 1. Detener todos los procesos
echo 2. Iniciar backend v62 (que funciona)
echo 3. Iniciar app Flutter
echo.
pause

echo.
echo [1/3] Iniciando Backend V62...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v62"
start "Backend V62" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5

echo.
echo [2/3] Esperando 5 segundos para que el backend inicie...
timeout /t 5

echo.
echo [3/3] Iniciando App Flutter...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_app"
start "Flutter App" cmd /k "set PATH=%PATH%;C:\Users\kevin\flutter\bin && flutter run -d chrome"

echo.
echo ============================================
echo  SISTEMA INICIADO
echo ============================================
echo.
echo Backend: http://localhost:8000
echo App: Se abrira automaticamente en Chrome
echo.
echo Presiona cualquier tecla para cerrar esta ventana
pause
