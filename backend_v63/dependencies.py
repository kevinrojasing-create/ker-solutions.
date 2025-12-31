"""
Dependencies - Common dependencies for routers
Refactored to check auth imports from central auth module
"""
from auth import get_current_user, require_role, get_current_active_user
from database import get_db

__all__ = ["get_current_user", "require_role", "get_current_active_user", "get_db"]
