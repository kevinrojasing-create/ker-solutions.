"""
SQLAlchemy Models - V63 Simplified SaaS + IoT
Core models only: Auth, Tenancy, Assets, Tickets, IoT
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime


# ============================================================================
# ENUMS - V63 Simplified
# ============================================================================

class SubscriptionPlan(str, enum.Enum):
    """Commercial subscription plans - MVP Tiers"""
    FREE = "free"                # $0 - Max 1 asset, basic diagnosis (no cost estimate)
    DIGITAL = "digital"          # $14,990 - 20 assets, OCR, QR codes, cost estimation, legal alerts
    MONITOR = "monitor"          # $24,990 - Digital + Human support, PDF reports, roles, IoT visualization
    CONTROL_TOTAL = "control_total"  # $34,990 - Monitor + Remote control (ON/OFF), scheduling

class UserRole(str, enum.Enum):
    """User roles"""
    OWNER = "owner"
    STAFF = "staff"
    TECHNICIAN = "technician"


class AssetStatus(str, enum.Enum):
    """Asset operational status"""
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    DOWN = "down"


class TicketStatus(str, enum.Enum):
    """Service ticket workflow states"""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TicketPriority(str, enum.Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeviceType(str, enum.Enum):
    """IoT device types"""
    TEMP_HUM = "temp_hum"        # SNZB-02D
    ENERGY = "energy"            # POW Origin
    BRIDGE = "bridge"            # Zigbee Bridge Pro


class AlertType(str, enum.Enum):
    """Alert types"""
    TEMPERATURE_HIGH = "temperature_high"
    TEMPERATURE_LOW = "temperature_low"
    HUMIDITY_HIGH = "humidity_high"
    ENERGY_SPIKE = "energy_spike"
    DEVICE_OFFLINE = "device_offline"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class UrgencyLevel(str, enum.Enum):
    """Urgency semaphore for AI diagnosis"""
    GREEN = "green"      # Low urgency - Can wait
    YELLOW = "yellow"    # Medium urgency - Schedule soon
    RED = "red"          # High urgency - Immediate action


class MaintenanceType(str, enum.Enum):
    """Types of preventive maintenance"""
    EXTINTOR = "extintor"                  # Fire extinguisher
    CERTIFICACION = "certificacion"        # Certification
    LIMPIEZA = "limpieza"                  # Cleaning
    INSPECCION = "inspeccion"              # Inspection
    REVISION_ELECTRICA = "revision_electrica"  # Electrical review


# ============================================================================
# USERS & AUTHENTICATION
# ============================================================================

class User(Base):
    """Core user model with multi-role support"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(50))
    
    # Role & Status
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STAFF)
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.DIGITAL)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile
    profile_image_url = Column(String(500))
    company_name = Column(String(255))  # For OWNER role
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owned_locales = relationship("Local", back_populates="owner", foreign_keys="Local.owner_id")
    otp_codes = relationship("OTPCode", back_populates="user")


class OTPCode(Base):
    """One-time passwords for email/SMS verification"""
    __tablename__ = "otp_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)  # "email_verification", "password_reset"
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="otp_codes")


# ============================================================================
# TENANCY & LOCATIONS
# ============================================================================

class Local(Base):
    """Physical locations (stores, buildings, facilities)"""
    __tablename__ = "locales"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    
    # Visual
    floor_plan_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="owned_locales", foreign_keys=[owner_id])
    members = relationship("LocalMember", back_populates="local")
    assets = relationship("Asset", back_populates="local")
    iot_devices = relationship("IoTDevice", back_populates="local")


class LocalMember(Base):
    """Users with access to a specific location"""
    __tablename__ = "local_members"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(SQLEnum(UserRole), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    local = relationship("Local", back_populates="members")
    user = relationship("User")


# ============================================================================
# ASSETS
# ============================================================================

class Asset(Base):
    """Physical assets (equipment, machinery, refrigerators, AC units)"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    qr_code = Column(String(100), unique=True, index=True)
    brand = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    category = Column(String(100))  # "refrigerator", "ac_unit", "electrical", etc.
    image_url = Column(String(500))
    
    # Status
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.OPERATIONAL)
    health_score = Column(Integer, default=100)  # 0-100% health indicator
    
    # Dates
    installation_date = Column(DateTime(timezone=True))
    warranty_expiry = Column(DateTime(timezone=True))
    last_maintenance_date = Column(DateTime(timezone=True))
    
    # Map Position (for floor plan visualization)
    map_position_x = Column(Float)
    map_position_y = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    local = relationship("Local", back_populates="assets")
    tickets = relationship("ServiceTicket", back_populates="asset")


# ============================================================================
# SERVICE TICKETS
# ============================================================================

class ServiceTicket(Base):
    """Service tickets - the heart of operations"""
    __tablename__ = "service_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    
    # Ticket Info
    ticket_type = Column(String(50))  # "corrective", "preventive", "inspection"
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    description = Column(Text, nullable=False)
    
    # AI Diagnosis
    ai_diagnosis = Column(Text)
    estimated_cost_clp = Column(Integer)  # Estimated repair cost in Chilean Pesos
    urgency_level = Column(SQLEnum(UrgencyLevel))  # Traffic light: green/yellow/red
    recommended_action = Column(Text)  # AI recommended next steps
    
    # Work Dates
    visit_date = Column(DateTime(timezone=True))
    work_started_at = Column(DateTime(timezone=True))
    work_ended_at = Column(DateTime(timezone=True))
    
    # Completion
    technician_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    local = relationship("Local")
    requester = relationship("User", foreign_keys=[requester_id])
    assigned_technician = relationship("User", foreign_keys=[assigned_technician_id])
    asset = relationship("Asset", back_populates="tickets")
    attachments = relationship("TicketAttachment", back_populates="ticket")


class TicketAttachment(Base):
    """Photos, videos, documents attached to tickets"""
    __tablename__ = "ticket_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=False)
    
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50))  # "photo", "video", "pdf"
    description = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("ServiceTicket", back_populates="attachments")


# ============================================================================
# MAINTENANCE SCHEDULING (MVP FEATURE)
# ============================================================================

class MaintenanceSchedule(Base):
    """Preventive maintenance schedules for assets"""
    __tablename__ = "maintenance_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    # Maintenance Info
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    description = Column(Text)
    
    # Scheduling
    next_due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    frequency_days = Column(Integer)  # How often (e.g., 30, 90, 365 days)
    last_completed_date = Column(DateTime(timezone=True))
    
    # Evidence requirement
    evidence_required = Column(Boolean, default=True)  # Require photo to complete
    evidence_url = Column(String(500))  # Photo evidence when completed
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset")


class RepairCostEstimate(Base):
    """Lookup table for repair cost estimation (MVP - Chilean market)"""
    __tablename__ = "repair_cost_estimates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Classification
    category = Column(String(100), nullable=False, index=True)  # "refrigerator", "ac_unit", etc.
    problem_type = Column(String(255), nullable=False)  # "no cooling", "leaking", "noise"
    
    # Cost range in CLP (Chilean Pesos)
    min_cost_clp = Column(Integer, nullable=False)
    max_cost_clp = Column(Integer, nullable=False)
    avg_cost_clp = Column(Integer, nullable=False)
    
    # Additional info
    typical_duration_hours = Column(Float)  # Typical repair time
    urgency_guidance = Column(SQLEnum(UrgencyLevel))  # Typical urgency for this issue
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# IOT DEVICES & TELEMETRY
# ============================================================================

class IoTDevice(Base):
    """IoT sensors and devices (Zigbee, WiFi)"""
    __tablename__ = "iot_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # Optional link to asset
    
    # Device Info
    device_type = Column(SQLEnum(DeviceType), nullable=False)
    device_id = Column(String(100), unique=True, nullable=False, index=True)  # MAC address or unique ID
    name = Column(String(255), nullable=False)
    
    # Status
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True))
    
    # Thresholds for automatic alerts (MVP feature)
    temp_threshold_min = Column(Float)  # Minimum temperature (°C)
    temp_threshold_max = Column(Float)  # Maximum temperature (°C) 
    humidity_threshold_min = Column(Float)  # Minimum humidity (%)
    humidity_threshold_max = Column(Float)  # Maximum humidity (%)
    energy_threshold_max = Column(Float)  # Maximum energy consumption (kW)
    
    # Configuration (JSON for flexibility)
    config = Column(JSON, default={})  # e.g., {"alert_enabled": true}
    
    # Map Position
    map_position_x = Column(Float)
    map_position_y = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    local = relationship("Local", back_populates="iot_devices")
    asset = relationship("Asset")
    telemetry = relationship("Telemetry", back_populates="device")
    alerts = relationship("Alert", back_populates="device")


class Telemetry(Base):
    """Time-series data from IoT devices"""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("iot_devices.id"), nullable=False)
    
    # Data (JSON for flexibility - different sensors have different data)
    data = Column(JSON, nullable=False)  # e.g., {"temperature": 23.5, "humidity": 65}
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    device = relationship("IoTDevice", back_populates="telemetry")


# ============================================================================
# ALERTS
# ============================================================================

class Alert(Base):
    """Alerts generated by AI/rules from IoT data"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("iot_devices.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    
    # Alert Info
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Data that triggered the alert
    trigger_data = Column(JSON)  # e.g., {"temperature": 35, "threshold": 25}
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    local = relationship("Local")
    device = relationship("IoTDevice", back_populates="alerts")
    asset = relationship("Asset")
    acknowledged_by = relationship("User")


# ============================================================================
# AUDIT LOGS
# ============================================================================

class AuditLog(Base):
    """Comprehensive audit trail for all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)  # "create", "update", "delete", etc.
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=True)
    
    changes = Column(JSON)  # Before/after values
    ip_address = Column(String(50))
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
