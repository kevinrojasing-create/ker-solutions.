"""
Main FastAPI Application - V63 Simplified SaaS + IoT
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routers import auth, locales, assets, tickets, iot, alerts, dashboard, maintenance


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    
    # Initialize database (development only)
    if settings.ENVIRONMENT == "development":
        try:
            print("🔧 Initializing database tables...")
            await init_db()
            print("✅ Database ready")
        except Exception as e:
            print(f"⚠️  Database init warning: {e}")
            print("   (Tables may already exist - this is OK)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="KER Solutions V63 - Simplified SaaS + IoT Platform for Facility Management",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS - Explicit configuration for Flutter Web Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://localhost",
        "http://127.0.0.1",
        "*"  # Allow all origins in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(auth.router)
app.include_router(locales.router)
app.include_router(assets.router)
app.include_router(tickets.router)
app.include_router(iot.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(maintenance.router)





# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    API root - health check
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "features": {
            "auth": True,
            "multi_tenant": True,
            "iot": True,
            "alerts": True,
            "dashboard": True
        }
    }


@app.get("/system/version")
async def get_version():
    """
    Get system version information
    """
    return {
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "features": {
            "auth": True,
            "locales": True,
            "assets": True,
            "tickets": True,
            "iot": True,
            "alerts": True,
            "dashboard": True
        },
        "iot_devices_supported": [
            "Zigbee Bridge Pro",
            "POW Origin (Energy Sensor)",
            "SNZB-02D (Temp/Humidity Sensor)"
        ]
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )
