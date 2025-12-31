@echo off
set "PATH=%PATH%;C:\Users\kevin\flutter\bin"
echo ===================================================
echo   INICIANDO KER SOLUTIONS V63 FRONTEND (FLUTTER)
echo ===================================================
echo.
echo Asegurate de que el backend este corriendo en otra ventana.
echo Si no tienes un dispositivo movil conectado, se intentara abrir en Chrome.
echo.
echo Ejecutando 'flutter pub get' para instalar dependencias...
call flutter pub get

echo.
echo Iniciando aplicacion...
cmd /k "flutter run"
