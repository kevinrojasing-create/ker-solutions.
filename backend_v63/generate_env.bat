@echo off
echo Generando .env para V63...
(
echo DATABASE_URL=sqlite+aiosqlite:///./ker_v63.db
echo SECRET_KEY=dev_secret_key_v63_change_in_production_123456789
echo APP_NAME=KER Solutions V63
echo APP_VERSION=v63.0.0
echo ENVIRONMENT=development
echo CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000"]
echo ACCESS_TOKEN_EXPIRE_MINUTES=1440
) > .env
echo Archivo .env creado correctamente.
