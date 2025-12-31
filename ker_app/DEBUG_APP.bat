@echo off
set "PATH=%PATH%;C:\Users\kevin\flutter\bin"
echo ===================================================
echo   DIAGNOSTICO DE FLUTTER
echo ===================================================
echo.
echo 1. Verificando instalacion de Flutter...
call flutter --version
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro el comando 'flutter'.
    echo Asegurate de tener Flutter instalado y en el PATH.
    pause
    exit /b
)

echo.
echo 2. Verificando dispositivos conectados...
call flutter devices

echo.
echo 3. Intentando iniciar en Windows (Escritorio)...
echo    Si falla, intentaremos Chrome.
echo.
call flutter run -d windows -v > flutter_log.txt 2>&1

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al iniciar en Windows.
    echo Intentando iniciar en Chrome...
    call flutter run -d chrome -v >> flutter_log.txt 2>&1
)

echo.
echo Si ves esto, revisa el archivo 'flutter_log.txt' en esta carpeta
echo para ver el error detallado.
pause
