@echo off
set "PATH=%PATH%;C:\Users\kevin\flutter\bin"
echo ===================================================
echo   LIMPIANDO Y REPARANDO APP FLUTTER
echo ===================================================
echo.
echo Limpiando cache de compilacion...
call flutter clean
echo.
echo Obteniendo dependencias...
call flutter pub get
echo.
echo ===================================================
echo   LISTO! Ahora puedes ejecutar START_APP.bat
echo ===================================================
pause
