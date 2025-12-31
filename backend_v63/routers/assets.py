"""
Assets Router - Asset management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from sql_models import Asset as AssetModel, Local as LocalModel, Alert as AlertModel, User as UserModel
from schemas import Asset, AssetCreate, AssetUpdate, AssetHealth, MessageResponse
from dependencies import get_current_user


router = APIRouter(prefix="/assets", tags=["Assets"])


async def verify_local_access(local_id: int, user_id: int, db: AsyncSession):
    """Helper to verify user has access to local"""
    result = await db.execute(
        select(LocalModel).where(LocalModel.id == local_id)
    )
    local = result.scalar_one_or_none()
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    # Check if user is owner or member
    from sql_models import LocalMember as LocalMemberModel
    if local.owner_id != user_id:
        result = await db.execute(
            select(LocalMemberModel).where(
                LocalMemberModel.local_id == local_id,
                LocalMemberModel.user_id == user_id
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this local"
            )


@router.get("/", response_model=List[Asset])
async def list_assets(
    local_id: Optional[int] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all assets (optionally filtered by local_id)
    """
    query = select(AssetModel).where(AssetModel.deleted_at.is_(None))
    
    if local_id:
        await verify_local_access(local_id, current_user.id, db)
        query = query.where(AssetModel.local_id == local_id)
    else:
        # Get all locales user has access to
        from sql_models import LocalMember as LocalMemberModel
        result = await db.execute(
            select(LocalModel.id).where(LocalModel.owner_id == current_user.id)
        )
        owned_local_ids = [row[0] for row in result.all()]
        
        result = await db.execute(
            select(LocalMemberModel.local_id).where(LocalMemberModel.user_id == current_user.id)
        )
        member_local_ids = [row[0] for row in result.all()]
        
        accessible_local_ids = list(set(owned_local_ids + member_local_ids))
        query = query.where(AssetModel.local_id.in_(accessible_local_ids))
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return assets


@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new asset
    """
    await verify_local_access(asset_data.local_id, current_user.id, db)
    
    # Generate QR code (simple UUID for now)
    import uuid
    qr_code = f"ASSET-{uuid.uuid4().hex[:12].upper()}"
    
    new_asset = AssetModel(
        **asset_data.model_dump(),
        qr_code=qr_code
    )
    
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    
    return new_asset


@router.get("/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get asset details
    """
    result = await db.execute(
        select(AssetModel).where(
            AssetModel.id == asset_id,
            AssetModel.deleted_at.is_(None)
        )
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    await verify_local_access(asset.local_id, current_user.id, db)
    
    return asset


@router.put("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update asset
    """
    result = await db.execute(
        select(AssetModel).where(
            AssetModel.id == asset_id,
            AssetModel.deleted_at.is_(None)
        )
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    await verify_local_access(asset.local_id, current_user.id, db)
    
    # Update fields
    for field, value in asset_data.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    
    await db.commit()
    await db.refresh(asset)
    
    return asset


@router.delete("/{asset_id}", response_model=MessageResponse)
async def delete_asset(
    asset_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete asset
    """
    result = await db.execute(
        select(AssetModel).where(
            AssetModel.id == asset_id,
            AssetModel.deleted_at.is_(None)
        )
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    await verify_local_access(asset.local_id, current_user.id, db)
    
    asset.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return MessageResponse(message="Asset deleted successfully")


@router.get("/{asset_id}/health", response_model=AssetHealth)
async def get_asset_health(
    asset_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get asset health score and metrics
    """
    result = await db.execute(
        select(AssetModel).where(
            AssetModel.id == asset_id,
            AssetModel.deleted_at.is_(None)
        )
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    await verify_local_access(asset.local_id, current_user.id, db)
    
    # Calculate health score
    health_score = 100
    
    # Reduce score based on status
    if asset.status == "maintenance":
        health_score -= 30
    elif asset.status == "down":
        health_score = 0
    
    # Calculate days since last maintenance
    days_since_maintenance = None
    if asset.last_maintenance_date:
        days_since_maintenance = (datetime.utcnow() - asset.last_maintenance_date).days
        # Reduce score if maintenance is overdue (assuming 90 days interval)
        if days_since_maintenance > 90:
            health_score -= min(40, (days_since_maintenance - 90) // 10 * 10)
    
    # Check for active alerts
    result = await db.execute(
        select(func.count(AlertModel.id)).where(
            AlertModel.asset_id == asset_id,
            AlertModel.is_resolved == False
        )
    )
    alert_count = result.scalar() or 0
    has_active_alerts = alert_count > 0
    
    if has_active_alerts:
        health_score -= min(30, alert_count * 10)
    
    health_score = max(0, health_score)
    
    return AssetHealth(
        asset_id=asset.id,
        asset_name=asset.name,
        status=asset.status,
        health_score=health_score,
        days_since_maintenance=days_since_maintenance,
        has_active_alerts=has_active_alerts,
        alert_count=alert_count
    )
