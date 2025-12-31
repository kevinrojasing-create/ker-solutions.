"""
IoT Router - IoT device and telemetry management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timedelta
import json

from database import get_db
from sql_models import IoTDevice as DeviceModel, Telemetry as TelemetryModel, User as UserModel
from schemas import IoTDevice, IoTDeviceCreate, IoTDeviceUpdate, Telemetry, TelemetryCreate, TelemetryData, MessageResponse
from dependencies import get_current_user
from routers.assets import verify_local_access


router = APIRouter(prefix="/iot", tags=["IoT"])


@router.get("/devices", response_model=List[IoTDevice])
async def list_devices(
    local_id: Optional[int] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List IoT devices
    """
    query = select(DeviceModel).where(DeviceModel.deleted_at.is_(None))
    
    if local_id:
        await verify_local_access(local_id, current_user.id, db)
        query = query.where(DeviceModel.local_id == local_id)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return devices


@router.post("/devices", response_model=IoTDevice, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: IoTDeviceCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new IoT device
    """
    await verify_local_access(device_data.local_id, current_user.id, db)
    
    # Check if device_id already exists
    result = await db.execute(
        select(DeviceModel).where(DeviceModel.device_id == device_data.device_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device ID already registered"
        )
    
    new_device = DeviceModel(**device_data.model_dump())
    
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)
    
    return new_device


@router.get("/devices/{device_id}", response_model=IoTDevice)
async def get_device(
    device_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get device details
    """
    result = await db.execute(
        select(DeviceModel).where(
            DeviceModel.id == device_id,
            DeviceModel.deleted_at.is_(None)
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    await verify_local_access(device.local_id, current_user.id, db)
    
    return device


@router.put("/devices/{device_id}", response_model=IoTDevice)
async def update_device(
    device_id: int,
    device_data: IoTDeviceUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update device configuration
    """
    result = await db.execute(
        select(DeviceModel).where(
            DeviceModel.id == device_id,
            DeviceModel.deleted_at.is_(None)
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    await verify_local_access(device.local_id, current_user.id, db)
    
    # Update fields
    for field, value in device_data.model_dump(exclude_unset=True).items():
        setattr(device, field, value)
    
    await db.commit()
    await db.refresh(device)
    
    return device


@router.post("/telemetry", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def receive_telemetry(
    telemetry_data: TelemetryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive telemetry data from IoT device (webhook endpoint)
    No authentication required for devices
    """
    # Verify device exists
    result = await db.execute(
        select(DeviceModel).where(DeviceModel.id == telemetry_data.device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Update device heartbeat
    device.last_heartbeat = datetime.utcnow()
    device.is_online = True
    
    # Store telemetry
    new_telemetry = TelemetryModel(**telemetry_data.model_dump())
    db.add(new_telemetry)
    
    # Check for alerts (simple threshold checking)
    await check_and_create_alerts(device, telemetry_data.data, db)
    
    await db.commit()
    
    return MessageResponse(message="Telemetry received successfully")


@router.get("/telemetry/{device_id}", response_model=List[TelemetryData])
async def get_telemetry_history(
    device_id: int,
    hours: int = Query(24, description="Hours of history to retrieve"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get telemetry history for a device
    """
    # Verify device exists and user has access
    result = await db.execute(
        select(DeviceModel).where(DeviceModel.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    await verify_local_access(device.local_id, current_user.id, db)
    
    # Get telemetry
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(TelemetryModel)
        .where(
            TelemetryModel.device_id == device_id,
            TelemetryModel.timestamp >= since
        )
        .order_by(desc(TelemetryModel.timestamp))
        .limit(1000)  # Max 1000 records
    )
    telemetry_records = result.scalars().all()
    
    # Convert to simplified format
    telemetry_data = []
    for record in telemetry_records:
        telemetry_data.append(TelemetryData(
            timestamp=record.timestamp,
            temperature=record.data.get("temperature"),
            humidity=record.data.get("humidity"),
            energy=record.data.get("energy")
        ))
    
    return telemetry_data


async def check_and_create_alerts(device: DeviceModel, data: dict, db: AsyncSession):
    """
    Check telemetry data against thresholds and create alerts if needed
    """
    from sql_models import Alert as AlertModel, AlertType, AlertSeverity
    
    config = device.config or {}
    
    # Temperature high
    if "temperature" in data and "temp_threshold_high" in config:
        if data["temperature"] > config["temp_threshold_high"]:
            alert = AlertModel(
                local_id=device.local_id,
                device_id=device.id,
                asset_id=device.asset_id,
                alert_type=AlertType.TEMPERATURE_HIGH,
                severity=AlertSeverity.CRITICAL,
                title=f"Temperatura Alta - {device.name}",
                message=f"Temperatura de {data['temperature']}°C excede el umbral de {config['temp_threshold_high']}°C",
                trigger_data={"temperature": data["temperature"], "threshold": config["temp_threshold_high"]}
            )
            db.add(alert)
    
    # Temperature low
    if "temperature" in data and "temp_threshold_low" in config:
        if data["temperature"] < config["temp_threshold_low"]:
            alert = AlertModel(
                local_id=device.local_id,
                device_id=device.id,
                asset_id=device.asset_id,
                alert_type=AlertType.TEMPERATURE_LOW,
                severity=AlertSeverity.WARNING,
                title=f"Temperatura Baja - {device.name}",
                message=f"Temperatura de {data['temperature']}°C está por debajo del umbral de {config['temp_threshold_low']}°C",
                trigger_data={"temperature": data["temperature"], "threshold": config["temp_threshold_low"]}
            )
            db.add(alert)
    
    # Energy spike
    if "energy" in data and "energy_threshold" in config:
        if data["energy"] > config["energy_threshold"]:
            alert = AlertModel(
                local_id=device.local_id,
                device_id=device.id,
                asset_id=device.asset_id,
                alert_type=AlertType.ENERGY_SPIKE,
                severity=AlertSeverity.WARNING,
                title=f"Pico de Energía - {device.name}",
                message=f"Consumo de {data['energy']} kW excede el umbral de {config['energy_threshold']} kW",
                trigger_data={"energy": data["energy"], "threshold": config["energy_threshold"]}
            )
            db.add(alert)
