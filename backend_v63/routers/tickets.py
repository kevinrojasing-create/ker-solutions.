"""
Tickets Router - Service ticket management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from sql_models import (
    ServiceTicket as TicketModel,
    TicketAttachment as AttachmentModel,
    User as UserModel,
    TicketStatus
)
from schemas import (
    Ticket, TicketCreate, TicketUpdate, TicketAssign, TicketComplete,
    TicketAttachment, TicketAttachmentCreate, MessageResponse
)
from dependencies import get_current_user
from routers.assets import verify_local_access


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/", response_model=List[Ticket])
async def list_tickets(
    local_id: Optional[int] = Query(None),
    status: Optional[TicketStatus] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List tickets (filtered by local_id and/or status)
    """
    query = select(TicketModel).where(TicketModel.deleted_at.is_(None))
    
    if local_id:
        await verify_local_access(local_id, current_user.id, db)
        query = query.where(TicketModel.local_id == local_id)
    
    if status:
        query = query.where(TicketModel.status == status)
    
    query = query.order_by(TicketModel.created_at.desc())
    
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return tickets


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new service ticket
    """
    await verify_local_access(ticket_data.local_id, current_user.id, db)
    
    new_ticket = TicketModel(
        **ticket_data.model_dump(),
        requester_id=current_user.id
    )
    
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    
    return new_ticket


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ticket details
    """
    result = await db.execute(
        select(TicketModel).where(
            TicketModel.id == ticket_id,
            TicketModel.deleted_at.is_(None)
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await verify_local_access(ticket.local_id, current_user.id, db)
    
    return ticket


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update ticket
    """
    result = await db.execute(
        select(TicketModel).where(
            TicketModel.id == ticket_id,
            TicketModel.deleted_at.is_(None)
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await verify_local_access(ticket.local_id, current_user.id, db)
    
    # Update fields
    for field, value in ticket_data.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.post("/{ticket_id}/assign", response_model=Ticket)
async def assign_ticket(
    ticket_id: int,
    assign_data: TicketAssign,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign ticket to a technician
    """
    result = await db.execute(
        select(TicketModel).where(TicketModel.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await verify_local_access(ticket.local_id, current_user.id, db)
    
    ticket.assigned_technician_id = assign_data.technician_id
    ticket.visit_date = assign_data.visit_date
    ticket.status = TicketStatus.ASSIGNED
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.post("/{ticket_id}/complete", response_model=Ticket)
async def complete_ticket(
    ticket_id: int,
    complete_data: TicketComplete,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a ticket
    """
    result = await db.execute(
        select(TicketModel).where(TicketModel.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    from datetime import datetime
    ticket.technician_notes = complete_data.technician_notes
    ticket.status = TicketStatus.COMPLETED
    ticket.work_ended_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.post("/{ticket_id}/attachments", response_model=TicketAttachment, status_code=status.HTTP_201_CREATED)
async def add_attachment(
    ticket_id: int,
    attachment_data: TicketAttachmentCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add attachment to ticket
    """
    result = await db.execute(
        select(TicketModel).where(TicketModel.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    new_attachment = AttachmentModel(
        ticket_id=ticket_id,
        **attachment_data.model_dump()
    )
    
    db.add(new_attachment)
    await db.commit()
    await db.refresh(new_attachment)
    
    return new_attachment
