"""
Dashboard Router - Dashboard statistics and metrics
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta

from database import get_db
from sql_models import (
    Asset as AssetModel,
    ServiceTicket as TicketModel,
    Alert as AlertModel,
    IoTDevice as DeviceModel,
    Telemetry as TelemetryModel,
    User as UserModel,
    TicketStatus,
    DeviceType
)
from schemas import DashboardStats, EnergyStats, ClimateStats
from dependencies import get_current_user
from routers.assets import verify_local_access


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    local_id: int = Query(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get general dashboard statistics for a local
    """
    await verify_local_access(local_id, current_user.id, db)
    
    # Total assets
    result = await db.execute(
        select(func.count(AssetModel.id)).where(
            AssetModel.local_id == local_id,
            AssetModel.deleted_at.is_(None)
        )
    )
    total_assets = result.scalar() or 0
    
    # Total tickets
    result = await db.execute(
        select(func.count(TicketModel.id)).where(
            TicketModel.local_id == local_id,
            TicketModel.deleted_at.is_(None)
        )
    )
    total_tickets = result.scalar() or 0
    
    # Open tickets
    result = await db.execute(
        select(func.count(TicketModel.id)).where(
            TicketModel.local_id == local_id,
            TicketModel.status.in_([TicketStatus.OPEN, TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS]),
            TicketModel.deleted_at.is_(None)
        )
    )
    open_tickets = result.scalar() or 0
    
    # Active alerts
    result = await db.execute(
        select(func.count(AlertModel.id)).where(
            AlertModel.local_id == local_id,
            AlertModel.is_resolved == False
        )
    )
    active_alerts = result.scalar() or 0
    
    # Devices online
    result = await db.execute(
        select(func.count(DeviceModel.id)).where(
            DeviceModel.local_id == local_id,
            DeviceModel.is_online == True,
            DeviceModel.deleted_at.is_(None)
        )
    )
    devices_online = result.scalar() or 0
    
    # Total devices
    result = await db.execute(
        select(func.count(DeviceModel.id)).where(
            DeviceModel.local_id == local_id,
            DeviceModel.deleted_at.is_(None)
        )
    )
    devices_total = result.scalar() or 0
    
    return DashboardStats(
        total_assets=total_assets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        active_alerts=active_alerts,
        devices_online=devices_online,
        devices_total=devices_total
    )


@router.get("/energy", response_model=EnergyStats)
async def get_energy_stats(
    local_id: int = Query(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get energy consumption statistics from POW Origin sensors
    """
    await verify_local_access(local_id, current_user.id, db)
    
    # Get all energy devices (POW Origin)
    result = await db.execute(
        select(DeviceModel).where(
            DeviceModel.local_id == local_id,
            DeviceModel.device_type == DeviceType.ENERGY,
            DeviceModel.deleted_at.is_(None)
        )
    )
    energy_devices = result.scalars().all()
    
    if not energy_devices:
        return EnergyStats(
            current_consumption=0.0,
            average_consumption=0.0,
            peak_consumption=0.0,
            total_today=0.0
        )
    
    device_ids = [d.id for d in energy_devices]
    
    # Get latest telemetry for current consumption
    current_consumption = 0.0
    for device_id in device_ids:
        result = await db.execute(
            select(TelemetryModel)
            .where(TelemetryModel.device_id == device_id)
            .order_by(TelemetryModel.timestamp.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        if latest and "energy" in latest.data:
            current_consumption += latest.data["energy"]
    
    # Get today's data for average and peak
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(TelemetryModel)
        .where(
            TelemetryModel.device_id.in_(device_ids),
            TelemetryModel.timestamp >= today_start
        )
    )
    today_telemetry = result.scalars().all()
    
    energy_values = [t.data.get("energy", 0) for t in today_telemetry if "energy" in t.data]
    
    average_consumption = sum(energy_values) / len(energy_values) if energy_values else 0.0
    peak_consumption = max(energy_values) if energy_values else 0.0
    
    # Calculate total kWh today (simplified - assumes readings every 5 min)
    total_today = sum(energy_values) * (5/60) if energy_values else 0.0  # kWh
    
    return EnergyStats(
        current_consumption=round(current_consumption, 2),
        average_consumption=round(average_consumption, 2),
        peak_consumption=round(peak_consumption, 2),
        total_today=round(total_today, 2),
        cost_estimate=round(total_today * 0.15, 2) if total_today > 0 else None  # $0.15/kWh estimate
    )


@router.get("/climate", response_model=ClimateStats)
async def get_climate_stats(
    local_id: int = Query(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get climate statistics from SNZB-02D sensors
    """
    await verify_local_access(local_id, current_user.id, db)
    
    # Get all temp/hum devices (SNZB-02D)
    result = await db.execute(
        select(DeviceModel).where(
            DeviceModel.local_id == local_id,
            DeviceModel.device_type == DeviceType.TEMP_HUM,
            DeviceModel.deleted_at.is_(None)
        )
    )
    climate_devices = result.scalars().all()
    
    if not climate_devices:
        return ClimateStats(
            average_temperature=0.0,
            average_humidity=0.0,
            min_temperature=0.0,
            max_temperature=0.0,
            devices_count=0
        )
    
    device_ids = [d.id for d in climate_devices]
    
    # Get last hour's data
    since = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(TelemetryModel)
        .where(
            TelemetryModel.device_id.in_(device_ids),
            TelemetryModel.timestamp >= since
        )
    )
    recent_telemetry = result.scalars().all()
    
    temperatures = [t.data.get("temperature", 0) for t in recent_telemetry if "temperature" in t.data]
    humidities = [t.data.get("humidity", 0) for t in recent_telemetry if "humidity" in t.data]
    
    return ClimateStats(
        average_temperature=round(sum(temperatures) / len(temperatures), 1) if temperatures else 0.0,
        average_humidity=round(sum(humidities) / len(humidities), 1) if humidities else 0.0,
        min_temperature=round(min(temperatures), 1) if temperatures else 0.0,
        max_temperature=round(max(temperatures), 1) if temperatures else 0.0,
        devices_count=len(climate_devices)
    )
