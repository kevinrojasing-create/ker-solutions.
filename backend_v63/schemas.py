"""
Pydantic Schemas - V63 Simplified
Request/Response models for API
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from sql_models import (
    UserRole, AssetStatus, TicketStatus, TicketPriority,
    DeviceType, AlertType, AlertSeverity, SubscriptionPlan,
    UrgencyLevel, MaintenanceType
)


# ============================================================================
# AUTHENTICATION
# ============================================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.OWNER
    plan: SubscriptionPlan = SubscriptionPlan.DIGITAL
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: "User"


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str = Field(min_length=8)


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str
    purpose: str  # "email_verification" or "password_reset"


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str
    role: Optional[str] = None


# ============================================================================
# USER
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: UserRole
    plan: SubscriptionPlan
    company_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    profile_image_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LOCAL (LOCATION)
# ============================================================================

class LocalBase(BaseModel):
    name: str
    address: str
    floor_plan_url: Optional[str] = None


class LocalCreate(LocalBase):
    pass


class LocalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    floor_plan_url: Optional[str] = None


class Local(LocalBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LocalMemberCreate(BaseModel):
    user_id: int
    role: UserRole


class LocalMember(BaseModel):
    id: int
    local_id: int
    user_id: int
    role: UserRole
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ASSET
# ============================================================================

class AssetBase(BaseModel):
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    status: AssetStatus = AssetStatus.OPERATIONAL
    health_score: int = 100
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    map_position_x: Optional[float] = None
    map_position_y: Optional[float] = None


class AssetCreate(AssetBase):
    local_id: int


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[AssetStatus] = None
    health_score: Optional[int] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    map_position_x: Optional[float] = None
    map_position_y: Optional[float] = None


class Asset(AssetBase):
    id: int
    local_id: int
    qr_code: Optional[str] = None
    last_maintenance_date: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AssetHealth(BaseModel):
    asset_id: int
    asset_name: str
    status: AssetStatus
    health_score: int  # 0-100
    days_since_maintenance: Optional[int] = None
    has_active_alerts: bool = False
    alert_count: int = 0


# ============================================================================
# SERVICE TICKET
# ============================================================================

class TicketBase(BaseModel):
    description: str
    ticket_type: Optional[str] = "corrective"
    priority: TicketPriority = TicketPriority.MEDIUM
    asset_id: Optional[int] = None


class TicketCreate(TicketBase):
    local_id: int


class TicketUpdate(BaseModel):
    description: Optional[str] = None
    ticket_type: Optional[str] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_technician_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    technician_notes: Optional[str] = None


class TicketAssign(BaseModel):
    technician_id: int
    visit_date: Optional[datetime] = None


class TicketComplete(BaseModel):
    technician_notes: str


class Ticket(TicketBase):
    id: int
    local_id: int
    requester_id: int
    assigned_technician_id: Optional[int] = None
    status: TicketStatus
    ai_diagnosis: Optional[str] = None
    visit_date: Optional[datetime] = None
    work_started_at: Optional[datetime] = None
    work_ended_at: Optional[datetime] = None
    technician_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TicketAttachmentCreate(BaseModel):
    file_url: str
    file_type: str  # "photo", "video", "pdf"
    description: Optional[str] = None


class TicketAttachment(TicketAttachmentCreate):
    id: int
    ticket_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# IOT DEVICE
# ============================================================================

class IoTDeviceBase(BaseModel):
    device_type: DeviceType
    device_id: str  # MAC address or unique ID
    name: str
    asset_id: Optional[int] = None
    config: Optional[dict] = {}
    map_position_x: Optional[float] = None
    map_position_y: Optional[float] = None


class IoTDeviceCreate(IoTDeviceBase):
    local_id: int


class IoTDeviceUpdate(BaseModel):
    name: Optional[str] = None
    asset_id: Optional[int] = None
    config: Optional[dict] = None
    map_position_x: Optional[float] = None
    map_position_y: Optional[float] = None


class IoTDevice(IoTDeviceBase):
    id: int
    local_id: int
    is_online: bool
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TelemetryCreate(BaseModel):
    device_id: int
    data: dict  # e.g., {"temperature": 23.5, "humidity": 65}


class Telemetry(TelemetryCreate):
    id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TelemetryData(BaseModel):
    """Simplified telemetry for charts"""
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    energy: Optional[float] = None


# ============================================================================
# ALERTS
# ============================================================================

class AlertCreate(BaseModel):
    local_id: int
    device_id: Optional[int] = None
    asset_id: Optional[int] = None
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    trigger_data: Optional[dict] = None


class AlertUpdate(BaseModel):
    is_acknowledged: Optional[bool] = None
    is_resolved: Optional[bool] = None


class Alert(BaseModel):
    id: int
    local_id: int
    device_id: Optional[int] = None
    asset_id: Optional[int] = None
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    trigger_data: Optional[dict] = None
    is_acknowledged: bool
    is_resolved: bool
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AlertRule(BaseModel):
    """Configuration for alert rules"""
    device_type: DeviceType
    alert_type: AlertType
    threshold_value: float
    comparison: str  # "gt", "lt", "eq"
    severity: AlertSeverity


# ============================================================================
# DASHBOARD
# ============================================================================

class DashboardStats(BaseModel):
    total_assets: int
    total_tickets: int
    open_tickets: int
    active_alerts: int
    devices_online: int
    devices_total: int


class EnergyStats(BaseModel):
    current_consumption: float  # kW
    average_consumption: float  # kW
    peak_consumption: float  # kW
    total_today: float  # kWh
    cost_estimate: Optional[float] = None  # $


class ClimateStats(BaseModel):
    average_temperature: float  # °C
    average_humidity: float  # %
    min_temperature: float
    max_temperature: float
    devices_count: int
# ============================================================================
# AI DIAGNOSIS & COST ESTIMATION (MVP)
# ============================================================================

class AIDiagnosisRequest(BaseModel):
    """Request for AI diagnosis based on problem photo"""
    image_url: str
    problem_description: Optional[str] = None
    asset_category: Optional[str] = None


class AIDiagnosisResponse(BaseModel):
    """AI diagnosis response with urgency and cost estimate"""
    diagnosis: str
    urgency_level: UrgencyLevel  # green, yellow, red
    estimated_cost_clp: Optional[int] = None  # Chilean Pesos
    cost_range_clp: Optional[str] = None  # e.g., "$50,000 - $150,000"
    recommended_action: str
    confidence_score: Optional[float] = None  # 0-1


# ============================================================================
# OCR FOR ASSET REGISTRATION (MVP)
# ============================================================================

class OCRScanRequest(BaseModel):
    """Request to scan placa técnica"""
    image_url: str


class OCRScanResponse(BaseModel):
    """Extracted data from placa técnica"""
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    raw_text: str  # Full OCR output
    confidence: float  # 0-1


# ============================================================================
# MAINTENANCE SCHEDULING (MVP)
# ============================================================================

class MaintenanceScheduleBase(BaseModel):
    maintenance_type: MaintenanceType
    description: Optional[str] = None
    next_due_date: datetime
    frequency_days: int
    evidence_required: bool = True


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
   asset_id: int


class MaintenanceScheduleUpdate(BaseModel):
    next_due_date: Optional[datetime] = None
    frequency_days: Optional[int] = None
    is_active: Optional[bool] = None


class MaintenanceSchedule(MaintenanceScheduleBase):
    id: int
    asset_id: int
    last_completed_date: Optional[datetime] = None
    evidence_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MaintenanceCompleteRequest(BaseModel):
    """Request to mark maintenance as complete"""
    evidence_url: str  # Required photo evidence


# ============================================================================
# PLAN LIMITS & FEATURE ACCESS (MVP)
# ============================================================================

class PlanLimits(BaseModel):
    """Feature limits based on subscription plan"""
    plan: SubscriptionPlan
    max_assets: Optional[int] = None  # None = unlimited
    ocr_enabled: bool
    cost_estimation_enabled: bool
    iot_visualization_enabled: bool
    remote_control_enabled: bool
    human_support_enabled: bool
    pdf_reports_enabled: bool


class FeatureAccessResponse(BaseModel):
    """Response indicating if user can access a feature"""
    has_access: bool
    reason: Optional[str] = None
    upgrade_plan: Optional[SubscriptionPlan] = None


# ============================================================================
# HEALTH SEMAPHORE (MVP)
# ============================================================================

class HealthStatusResponse(BaseModel):
    """Overall health status of a locale (traffic light)"""
    status: str  # "green", "yellow", "red"
    asset_issues: int  # Assets not operational
    critical_alerts: int  # Unresolved critical alerts
    overdue_maintenance: int  # Overdue maintenance tasks
    devices_offline: int  # IoT devices offline
    overall_health_score: int  # 0-100
