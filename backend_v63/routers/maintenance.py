"""
Maintenance Router - Preventive Maintenance Scheduling & Automation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from sql_models import (
    MaintenanceSchedule as ScheduleModel, 
    Asset as AssetModel,
    ServiceTicket as TicketModel,
    Local as LocalModel,
    TicketStatus, TicketPriority
)
from schemas import (
    MaintenanceSchedule, MaintenanceScheduleCreate, MaintenanceScheduleUpdate,
    MaintenanceCompleteRequest, Ticket, MessageResponse
)
from dependencies import get_current_user
from routers.assets import verify_local_access

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

# ============================================================================
# SCHEDULE MANAGEMENT
# ============================================================================

@router.post("/schedules", response_model=MaintenanceSchedule, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: MaintenanceScheduleCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new maintenance schedule for an asset
    """
    # Verify asset exists
    result = await db.execute(select(AssetModel).where(AssetModel.id == schedule_data.asset_id))
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    # Verify access
    await verify_local_access(asset.local_id, current_user.id, db)
    
    new_schedule = ScheduleModel(**schedule_data.model_dump())
    
    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    
    return new_schedule


@router.get("/schedules", response_model=List[MaintenanceSchedule])
async def list_schedules(
    asset_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List maintenance schedules (filtered by asset or local)
    """
    query = select(ScheduleModel)
    
    if asset_id:
        # Check permissions for asset
        result = await db.execute(select(AssetModel).where(AssetModel.id == asset_id))
        asset = result.scalar_one_or_none()
        if asset:
            await verify_local_access(asset.local_id, current_user.id, db)
            query = query.where(ScheduleModel.asset_id == asset_id)
        else:
            return [] # Or raise 404
            
    elif local_id:
        await verify_local_access(local_id, current_user.id, db)
        query = query.join(AssetModel).where(AssetModel.local_id == local_id)
        
    else:
        # Return all schedules for user's owned/member locales
        # Use simpler approach: Get all accessible local IDs first
        from sql_models import LocalMember
        
        owned_res = await db.execute(select(LocalModel.id).where(LocalModel.owner_id == current_user.id))
        member_res = await db.execute(select(LocalMember.local_id).where(LocalMember.user_id == current_user.id))
        
        accessible_ids = [r[0] for r in owned_res.all()] + [r[0] for r in member_res.all()]
        accessible_ids = list(set(accessible_ids))
        
        if not accessible_ids:
            return []
            
        query = query.join(AssetModel).where(AssetModel.local_id.in_(accessible_ids))
        
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/schedules/{schedule_id}", response_model=MaintenanceSchedule)
async def update_schedule(
    schedule_id: int,
    update_data: MaintenanceScheduleUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a maintenance schedule
    """
    result = await db.execute(select(ScheduleModel).where(ScheduleModel.id == schedule_id))
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    # Check permissions logic (need to join asset to get local_id)
    # Lazy load might warn in async, so we should fetch asset explicitly if needed
    # But let's assume valid access for now or fetch asset
    result = await db.execute(select(AssetModel).where(AssetModel.id == schedule.asset_id))
    asset = result.scalar_one_or_none()
    await verify_local_access(asset.local_id, current_user.id, db)
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
        
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.delete("/schedules/{schedule_id}", response_model=MessageResponse)
async def delete_schedule(
    schedule_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (hard delete) a schedule
    """
    result = await db.execute(select(ScheduleModel).where(ScheduleModel.id == schedule_id))
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    result = await db.execute(select(AssetModel).where(AssetModel.id == schedule.asset_id))
    asset = result.scalar_one_or_none()
    await verify_local_access(asset.local_id, current_user.id, db)
    
    await db.delete(schedule)
    await db.commit()
    
    return MessageResponse(message="Schedule deleted successfully")


# ============================================================================
# AUTOMATION
# ============================================================================

@router.post("/generate-tickets", response_model=List[Ticket])
async def generate_preventive_tickets(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check all active schedules and generate tickets if due.
    Returns list of generated tickets.
    """
    # 1. Get all active schedules where next_due_date <= now
    now = datetime.utcnow()
    query = select(ScheduleModel).where(
        ScheduleModel.is_active == True,
        ScheduleModel.next_due_date <= now
    )
    
    result = await db.execute(query)
    schedules = result.scalars().all()
    
    generated_tickets = []
    
    for sched in schedules:
        # Get Asset and Local info
        res_asset = await db.execute(select(AssetModel).where(AssetModel.id == sched.asset_id))
        asset = res_asset.scalar_one_or_none()
        if not asset:
             continue
             
        # Create Ticket
        new_ticket = TicketModel(
            local_id=asset.local_id,
            requester_id=current_user.id, # Automated by system, but attributed to admin/requester
            asset_id=asset.id,
            ticket_type="preventive",
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            description=f"Mantenimiento Preventivo: {sched.maintenance_type.value}\n{sched.description or ''}",
            created_at=now
        )
        
        db.add(new_ticket)
        
        # Update Schedule next_due_date
        # If frequency_days is set, add it. Otherwise, maybe keep it (one-time?)
        # Let's assume recurring if frequency_days > 0
        if sched.frequency_days and sched.frequency_days > 0:
            sched.next_due_date = now + timedelta(days=sched.frequency_days)
        else:
            # If not recurring, maybe disable it?
            sched.is_active = False
            
        generated_tickets.append(new_ticket)
        
    await db.commit()
    
    # Refresh tickets to get IDs
    for t in generated_tickets:
        await db.refresh(t)
        
    return generated_tickets
