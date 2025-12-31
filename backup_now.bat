@echo off
setlocal
:: Obtener fecha y hora para el nombre del archivo
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "datetime=%%I"
set "timestamp=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%"

set "BACKUP_DIR=backups"
set "SOURCE_DIR=ker_saas"
set "ZIP_NAME=ker_saas_v%timestamp%.zip"

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo ==================================================
echo   KER SOLUTIONS - SISTEMA DE RESPALDO AUTOMATICO
echo ==================================================
echo.
echo [1/3] Identificando archivos fuente en: %SOURCE_DIR%
echo [2/3] Comprimiendo hacia: %BACKUP_DIR%\%ZIP_NAME%
echo.
echo       Por favor espere, esto puede tomar unos segundos...

:: Usar PowerShell para comprimir (excluyendo carpetas pesadas innecesarias si fuera necesario, pero por seguridad guardamos todo)
powershell -command "Compress-Archive -Path '%SOURCE_DIR%' -DestinationPath '%BACKUP_DIR%\%ZIP_NAME%' -Force"

echo.
echo [3/3] Respaldo COMPLETADO EXITOSAMENTE.
echo.
echo Archivo guardado: %BACKUP_DIR%\%ZIP_NAME%
echo.
pause
