"""
Main FastAPI Application - V62 Core
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routers import auth


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
        print("🔧 Initializing database tables...")
        await init_db()
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Facility Management Platform with IoT, AI, and Multi-Tenant Support",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(auth.router)


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
        "environment": settings.ENVIRONMENT
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
            "multi_tenant": True,
            "async_db": True,
            "jwt": True
        }
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "detail": "Resource not found",
        "path": str(request.url)
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "detail": "Internal server error",
        "message": "An unexpected error occurred"
    }


# ============================================================================
# READY FOR EXPANSION
# ============================================================================
# Future routers to be added:
# - app.include_router(tickets.router)
# - app.include_router(assets.router)
# - app.include_router(inventory.router)
# - app.include_router(training.router)  # LMS
# - app.include_router(visitors.router)  # VMS
# - app.include_router(analytics.router)
