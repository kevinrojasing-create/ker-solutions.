"""
Alerts Router - Alert management and rules
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from database import get_db
from sql_models import Alert as AlertModel, User as UserModel, AlertSeverity
from schemas import Alert, AlertCreate, AlertUpdate, MessageResponse
from dependencies import get_current_user
from routers.assets import verify_local_access


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[Alert])
async def list_alerts(
    local_id: Optional[int] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List alerts (filtered by local_id, resolution status, and/or severity)
    """
    query = select(AlertModel)
    
    if local_id:
        await verify_local_access(local_id, current_user.id, db)
        query = query.where(AlertModel.local_id == local_id)
    
    if is_resolved is not None:
        query = query.where(AlertModel.is_resolved == is_resolved)
    
    if severity:
        query = query.where(AlertModel.severity == severity)
    
    query = query.order_by(AlertModel.created_at.desc())
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return alerts


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert details
    """
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    await verify_local_access(alert.local_id, current_user.id, db)
    
    return alert


@router.put("/{alert_id}/acknowledge", response_model=Alert)
async def acknowledge_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark alert as acknowledged
    """
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    await verify_local_access(alert.local_id, current_user.id, db)
    
    alert.is_acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by_id = current_user.id
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.put("/{alert_id}/resolve", response_model=Alert)
async def resolve_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark alert as resolved
    """
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    await verify_local_access(alert.local_id, current_user.id, db)
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(alert)
    
    return alert
