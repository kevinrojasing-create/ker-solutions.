"""
Locales Router - Location management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from sql_models import Local as LocalModel, LocalMember as LocalMemberModel, User as UserModel
from schemas import Local, LocalCreate, LocalUpdate, LocalMember, LocalMemberCreate, MessageResponse
from dependencies import get_current_user


router = APIRouter(prefix="/locales", tags=["Locales"])


@router.get("/", response_model=List[Local])
async def list_locales(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all locales owned by or accessible to the current user
    """
    # Get owned locales
    result = await db.execute(
        select(LocalModel).where(
            LocalModel.owner_id == current_user.id,
            LocalModel.deleted_at.is_(None)
        )
    )
    owned_locales = result.scalars().all()
    
    # Get locales where user is a member
    result = await db.execute(
        select(LocalModel)
        .join(LocalMemberModel)
        .where(
            LocalMemberModel.user_id == current_user.id,
            LocalModel.deleted_at.is_(None)
        )
    )
    member_locales = result.scalars().all()
    
    # Combine and deduplicate
    all_locales = list({loc.id: loc for loc in owned_locales + member_locales}.values())
    
    return all_locales


@router.post("/", response_model=Local, status_code=status.HTTP_201_CREATED)
async def create_local(
    local_data: LocalCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new local (only owners can create)
    """
    new_local = LocalModel(
        **local_data.model_dump(),
        owner_id=current_user.id
    )
    
    db.add(new_local)
    await db.commit()
    await db.refresh(new_local)
    
    return new_local


@router.get("/{local_id}", response_model=Local)
async def get_local(
    local_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get local details
    """
    result = await db.execute(
        select(LocalModel).where(
            LocalModel.id == local_id,
            LocalModel.deleted_at.is_(None)
        )
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    # Check access
    if local.owner_id != current_user.id:
        # Check if user is a member
        result = await db.execute(
            select(LocalMemberModel).where(
                LocalMemberModel.local_id == local_id,
                LocalMemberModel.user_id == current_user.id
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return local


@router.put("/{local_id}", response_model=Local)
async def update_local(
    local_id: int,
    local_data: LocalUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update local (only owner can update)
    """
    result = await db.execute(
        select(LocalModel).where(
            LocalModel.id == local_id,
            LocalModel.deleted_at.is_(None)
        )
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    if local.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can update local"
        )
    
    # Update fields
    for field, value in local_data.model_dump(exclude_unset=True).items():
        setattr(local, field, value)
    
    await db.commit()
    await db.refresh(local)
    
    return local


@router.delete("/{local_id}", response_model=MessageResponse)
async def delete_local(
    local_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete local (only owner can delete)
    """
    result = await db.execute(
        select(LocalModel).where(
            LocalModel.id == local_id,
            LocalModel.deleted_at.is_(None)
        )
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    if local.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete local"
        )
    
    from datetime import datetime
    local.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return MessageResponse(message="Local deleted successfully")


# ============================================================================
# MEMBERS
# ============================================================================

@router.get("/{local_id}/members", response_model=List[LocalMember])
async def list_members(
    local_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all members of a local
    """
    # Verify access to local
    result = await db.execute(
        select(LocalModel).where(LocalModel.id == local_id)
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    # Get members
    result = await db.execute(
        select(LocalMemberModel).where(LocalMemberModel.local_id == local_id)
    )
    members = result.scalars().all()
    
    return members


@router.post("/{local_id}/members", response_model=LocalMember, status_code=status.HTTP_201_CREATED)
async def add_member(
    local_id: int,
    member_data: LocalMemberCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a member to local (only owner can add)
    """
    # Verify local exists and user is owner
    result = await db.execute(
        select(LocalModel).where(LocalModel.id == local_id)
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    if local.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can add members"
        )
    
    # Check if user exists
    result = await db.execute(
        select(UserModel).where(UserModel.id == member_data.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a member
    result = await db.execute(
        select(LocalMemberModel).where(
            LocalMemberModel.local_id == local_id,
            LocalMemberModel.user_id == member_data.user_id
        )
    )
    existing_member = result.scalar_one_or_none()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    # Add member
    new_member = LocalMemberModel(
        local_id=local_id,
        **member_data.model_dump()
    )
    
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    
    return new_member


@router.delete("/{local_id}/members/{user_id}", response_model=MessageResponse)
async def remove_member(
    local_id: int,
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a member from local (only owner can remove)
    """
    # Verify local exists and user is owner
    result = await db.execute(
        select(LocalModel).where(LocalModel.id == local_id)
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    if local.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can remove members"
        )
    
    # Find and delete member
    result = await db.execute(
        select(LocalMemberModel).where(
            LocalMemberModel.local_id == local_id,
            LocalMemberModel.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    await db.delete(member)
    await db.commit()
    
    return MessageResponse(message="Member removed successfully")
