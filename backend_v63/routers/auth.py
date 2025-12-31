"""
Authentication Router - Registration, Login, OTP, Password Reset
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from database import get_db
from sql_models import User as UserModel, OTPCode as OTPCodeModel
from schemas import (
    User, UserCreate, RegisterRequest, LoginRequest, Token,
    PasswordResetRequest, PasswordResetConfirm, OTPVerifyRequest,
    MessageResponse
)
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    generate_otp_code
)
from config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# REGISTRATION
# ============================================================================

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user (DEVELOPMENT MODE - OTP BYPASSED)
    """
    try:
        # Check if user exists
        result = await db.execute(
            select(UserModel).where(UserModel.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        
        new_user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            role=user_data.role,
            plan=user_data.plan,
            company_name=user_data.company_name,
            is_active=True,
            is_verified=True  # DEV MODE: Skip OTP
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


# ============================================================================
# LOGIN
# ============================================================================

@router.post("/login")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password
    
    Returns JWT access token
    """
    user = await authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    # Return response directly as dict (FastAPI will convert to JSON)
    from fastapi.responses import JSONResponse
    return JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "role": user.role.value,
            "plan": user.plan.value,
            "company_name": user.company_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "profile_image_url": user.profile_image_url,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    })


# ============================================================================
# OTP VERIFICATION
# ============================================================================

@router.post("/verify-otp", response_model=MessageResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP code for email verification or password reset
    """
    # Get user
    result = await db.execute(
        select(UserModel).where(UserModel.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get OTP
    result = await db.execute(
        select(OTPCodeModel).where(
            OTPCodeModel.user_id == user.id,
            OTPCodeModel.code == request.code,
            OTPCodeModel.purpose == request.purpose,
            OTPCodeModel.is_used == False
        )
    )
    otp = result.scalar_one_or_none()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
    
    # Check expiration
    if otp.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code expired"
        )
    
    # Mark as used
    otp.is_used = True
    
    # If email verification, mark user as verified
    if request.purpose == "email_verification":
        user.is_verified = True
    
    await db.commit()
    
    return MessageResponse(
        message="OTP verified successfully",
        success=True
    )


# ============================================================================
# PASSWORD RESET
# ============================================================================

@router.post("/password-reset/request", response_model=MessageResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset - sends OTP to email
    """
    # Get user
    result = await db.execute(
        select(UserModel).where(UserModel.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if user exists
        return MessageResponse(
            message="If the email exists, a reset code has been sent",
            success=True
        )
    
    # Generate OTP
    otp_code = generate_otp_code()
    otp = OTPCodeModel(
        user_id=user.id,
        code=otp_code,
        purpose="password_reset",
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(otp)
    await db.commit()
    
    # TODO: Send email with OTP
    # await send_email(request.email, "Password Reset", f"Your code: {otp_code}")
    
    return MessageResponse(
        message="If the email exists, a reset code has been sent",
        success=True
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm password reset with OTP and set new password
    """
    # Verify OTP first
    await verify_otp(
        OTPVerifyRequest(
            email=request.email,
            code=request.otp_code,
            purpose="password_reset"
        ),
        db
    )
    
    # Get user
    result = await db.execute(
        select(UserModel).where(UserModel.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    await db.commit()
    
    return MessageResponse(
        message="Password reset successfully",
        success=True
    )


# ============================================================================
# RESEND OTP
# ============================================================================

@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(
    request: PasswordResetRequest,  # Reuse schema (just needs email)
    db: AsyncSession = Depends(get_db)
):
    """
    Resend OTP for email verification
    """
    # Get user
    result = await db.execute(
        select(UserModel).where(UserModel.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new OTP
    otp_code = generate_otp_code()
    otp = OTPCodeModel(
        user_id=user.id,
        code=otp_code,
        purpose="email_verification",
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(otp)
    await db.commit()
    
    # TODO: Send email
    # await send_email(request.email, "Verify your email", f"Your code: {otp_code}")
    
    return MessageResponse(
        message="OTP sent successfully",
        success=True
    )
