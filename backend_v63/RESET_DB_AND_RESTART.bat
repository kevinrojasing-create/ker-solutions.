@echo off
echo ===================================================
echo   REINICIANDO BASE DE DATOS PARA MVP COMERCIAL
echo ===================================================
echo.
echo ADVERTENCIA: Esto borrara la base de datos actual para aplicar los nuevos cambios (Planes de Suscripcion).
echo.
if exist ker_v63.db (
    echo Borrando ker_v63.db...
    del ker_v63.db
)
echo.
echo Reiniciando Backend...
START_SERVER.bat
