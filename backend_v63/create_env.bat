@echo off
echo DATABASE_URL=sqlite+aiosqlite:///./ker_v63.db > .env
echo SECRET_KEY=ker-solutions-v63-dev-secret-key-change-in-production >> .env
echo ALGORITHM=HS256 >> .env
echo ACCESS_TOKEN_EXPIRE_MINUTES=10080 >> .env
echo APP_NAME=KER Solutions V63 >> .env
echo APP_VERSION=63.0.0 >> .env
echo ENVIRONMENT=development >> .env
echo CORS_ORIGINS=http://localhost:3000,http://localhost:8080 >> .env
echo .env file created successfully!
