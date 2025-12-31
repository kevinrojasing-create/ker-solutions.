"""
Authentication & Security - JWT, Password Hashing, SSO
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from database import get_db
from sql_models import User as UserModel, APIKey as APIKeyModel
from schemas import TokenData, User
import secrets


# ============================================================================
# PASSWORD HASHING
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    Truncates to 72 bytes to comply with bcrypt limit
    """
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    password_str = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_str)


# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Payload to encode (must include 'sub' for user identifier)
        expires_delta: Token expiration time (default from settings)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData with user information
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None or email is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id, email=email, role=role)
        return token_data
        
    except JWTError:
        raise credentials_exception


# ============================================================================
# USER AUTHENTICATION
# ============================================================================

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[UserModel]:
    """
    Authenticate user with email and password
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
    
    Returns:
        User model if authenticated, None otherwise
    """
    result = await db.execute(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if not user.hashed_password:  # SSO user
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    Get current authenticated user from JWT token
    
    Dependency for protected routes:
        @app.get("/protected")
        async def protected_route(current_user: UserModel = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    token_data = decode_access_token(token)
    
    result = await db.execute(
        select(UserModel).where(UserModel.id == token_data.user_id, UserModel.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    Ensure user is active and verified
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: UserModel = Depends(require_role("admin", "owner"))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


# ============================================================================
# API KEY AUTHENTICATION
# ============================================================================

async def validate_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    Validate API key from X-API-Key header
    
    Usage:
        @app.get("/api/data")
        async def api_endpoint(user: UserModel = Depends(validate_api_key)):
            return {"data": "..."}
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    result = await db.execute(
        select(APIKeyModel).where(
            APIKeyModel.api_key == x_api_key,
            APIKeyModel.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check expiration
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired"
        )
    
    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    await db.commit()
    
    # Get user
    result = await db.execute(
        select(UserModel).where(UserModel.id == api_key.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"ker_{secrets.token_urlsafe(32)}"


def generate_otp_code(length: int = 6) -> str:
    """Generate a numeric OTP code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


# ============================================================================
# SSO HELPERS (Placeholder for future implementation)
# ============================================================================

async def authenticate_sso_user(
    provider: str,
    token: str,
    db: AsyncSession
) -> Optional[UserModel]:
    """
    Authenticate user via SSO provider
    
    TODO: Implement OAuth2 flows for:
    - Azure AD
    - Google Workspace
    - Okta
    - Auth0
    """
    # Placeholder for SSO implementation
    raise NotImplementedError("SSO authentication not yet implemented")
