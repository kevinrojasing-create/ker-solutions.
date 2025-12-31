"""
SQLAlchemy Models - V62 Core Foundation
Step 1: System, Auth & Tenant Management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime


# ============================================================================
# ENUMS - V62 Complete Set
# ============================================================================

class UserRole(str, enum.Enum):
    """User roles across the platform"""
    OWNER = "owner"
    STAFF = "staff"
    ADMIN = "admin"
    TECHNICIAN = "technician"
    GUARD = "guard"
    INCIDENT_COMMANDER = "incident_commander"
    WAREHOUSE_MANAGER = "warehouse_manager"
    PROCUREMENT_MANAGER = "procurement_manager"
    SUSTAINABILITY_MANAGER = "sustainability_manager"
    SAFETY_OFFICER = "safety_officer"
    BIM_MANAGER = "bim_manager"
    FINANCIAL_AUDITOR = "financial_auditor"
    TRAINING_MANAGER = "training_manager"


class PlanType(str, enum.Enum):
    """Subscription plan types"""
    DIGITAL = "digital"
    EXPERT = "expert"
    MONITOR_360 = "monitor_360"


# ============================================================================
# STEP 2: ASSETS & OPERATIONS ENUMS
# ============================================================================

class AssetStatus(str, enum.Enum):
    """Asset operational status"""
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    DOWN = "down"
    IN_STORAGE = "in_storage"
    DISPOSED = "disposed"


class ProductCategory(str, enum.Enum):
    """Product/Service categories"""
    HARDWARE_KIT = "hardware_kit"
    SENSOR_UNIT = "sensor_unit"
    SETUP_FEE = "setup_fee"
    CONSULTING_HOUR = "consulting_hour"
    SPARE_PART = "spare_part"


class TicketStatus(str, enum.Enum):
    """Service ticket workflow states"""
    OPEN = "open"
    QUOTING = "quoting"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    ASSIGNED = "assigned"
    OFFERED = "offered"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BILLED_IN_BATCH = "billed_in_batch"


class TicketPriority(str, enum.Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TechnicianSkill(str, enum.Enum):
    """Technician specializations"""
    ELECTRICITY = "electricity"
    HVAC = "hvac"
    PLUMBING = "plumbing"
    GENERAL = "general"
    IOT_INSTALL = "iot_install"


class ShiftType(str, enum.Enum):
    """Work shift types"""
    WORKING = "working"
    DAY_OFF = "day_off"
    SICK_LEAVE = "sick_leave"
    VACATION = "vacation"


# ============================================================================
# STEP 3: FINANCE & SUPPLY CHAIN ENUMS
# ============================================================================

class PaymentStatus(str, enum.Enum):
    """Payment transaction status"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class RequisitionStatus(str, enum.Enum):
    """Purchase requisition workflow"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ORDERED = "ordered"


class POStatus(str, enum.Enum):
    """Purchase Order status"""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_RECEIVED = "partially_received"
    FULLY_RECEIVED = "fully_received"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class ContractStatus(str, enum.Enum):
    """Contract lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class MovementType(str, enum.Enum):
    """Inventory movement types"""
    PURCHASE = "purchase"
    TRANSFER = "transfer"
    CONSUMPTION = "consumption"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class AdjustmentIndex(str, enum.Enum):
    """Contract price adjustment indices"""
    CPI = "cpi"  # Consumer Price Index
    UF = "uf"    # Unidad de Fomento (Chile)
    FIXED_PERCENTAGE = "fixed_percentage"
    NONE = "none"


# ============================================================================
# STEP 4: HSE, LMS & VMS ENUMS
# ============================================================================

class RiskLevel(str, enum.Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class LotoStatus(str, enum.Enum):
    """Lock-Out Tag-Out status"""
    ACTIVE = "active"
    REMOVED = "removed"


class TrainingStatus(str, enum.Enum):
    """Training completion status"""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"


class VisitorStatus(str, enum.Enum):
    """Visitor lifecycle status"""
    INVITED = "invited"
    PRE_REGISTERED = "pre_registered"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    BLACKLISTED = "blacklisted"


class AccessType(str, enum.Enum):
    """Type of facility access"""
    VISITOR = "visitor"
    CONTRACTOR = "contractor"
    DELIVERY = "delivery"
    EMPLOYEE = "employee"


class EmissionScope(str, enum.Enum):
    """GHG Protocol emission scopes"""
    SCOPE_1 = "scope_1"  # Direct emissions
    SCOPE_2 = "scope_2"  # Indirect (electricity)
    SCOPE_3 = "scope_3"  # Value chain


# ============================================================================
# STEP 5: ADVANCED FEATURES ENUMS (FINAL)
# ============================================================================

class BIMFormat(str, enum.Enum):
    """BIM model file formats"""
    IFC = "ifc"  # Industry Foundation Classes
    RVT = "rvt"  # Revit
    NWD = "nwd"  # Navisworks
    OBJ = "obj"  # Wavefront OBJ


class ReportType(str, enum.Enum):
    """Generated report types"""
    MAINTENANCE_MONTHLY = "maintenance_monthly"
    FINANCIAL_SUMMARY = "financial_summary"
    INCIDENT_REPORT = "incident_report"
    SLA_COMPLIANCE = "sla_compliance"
    ASSET_HEALTH = "asset_health"


class WidgetType(str, enum.Enum):
    """Dashboard widget types"""
    CHART_LINE = "chart_line"
    CHART_BAR = "chart_bar"
    CHART_PIE = "chart_pie"
    KPI_CARD = "kpi_card"
    LIST_RECENT = "list_recent"
    MAP_VIEW = "map_view"


class FailureCodeType(str, enum.Enum):
    """RCM failure code hierarchy"""
    PROBLEM = "problem"
    CAUSE = "cause"
    REMEDY = "remedy"


class RetentionStrategy(str, enum.Enum):
    """Data retention strategies"""
    DELETE = "delete"
    ARCHIVE_TO_COLD_STORAGE = "archive_to_cold_storage"


class DepreciationMethod(str, enum.Enum):
    """Asset depreciation methods"""
    STRAIGHT_LINE = "straight_line"
    DOUBLE_DECLINING = "double_declining"


# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

class SystemSetting(Base):
    """Global system settings (key-value store)"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(500))
    is_public = Column(Boolean, default=False)  # Can be exposed to frontend
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PlanLimit(Base):
    """Resource limits per subscription plan"""
    __tablename__ = "plan_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    resource = Column(String(100), nullable=False)  # e.g., "max_assets", "max_users"
    limit_value = Column(Integer, nullable=False)
    overage_price = Column(Float, nullable=True)  # Price per unit over limit
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {'comment': 'Defines resource limits for each subscription plan'}
    )


class AppVersion(Base):
    """Track mobile app versions for forced updates"""
    __tablename__ = "app_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False)  # "android", "ios", "web"
    version_number = Column(String(20), nullable=False)
    build_number = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=False)  # Force update
    release_notes = Column(Text)
    download_url = Column(String(500))
    
    released_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# USERS & AUTHENTICATION
# ============================================================================

class User(Base):
    """Core user model with multi-role support"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for SSO users
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(50))
    
    # Role & Status
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # SSO Integration
    sso_provider_id = Column(Integer, ForeignKey("identity_providers.id"), nullable=True)
    federated_id = Column(String(255), nullable=True)  # External user ID from SSO
    
    # Profile
    profile_image_url = Column(String(500))
    preferences = Column(JSON, default={})  # User preferences (theme, language, etc.)
    fcm_token = Column(String(500))  # Firebase Cloud Messaging token
    
    # Technician-specific
    technician_skills = Column(JSON, default=[])  # List of TechnicianSkill enums
    bank_details = Column(JSON)  # For payment processing
    
    # Company (for Owner role)
    company_name = Column(String(255))
    company_logo_url = Column(String(500))
    
    # Vendor link
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    owned_locales = relationship("Local", back_populates="owner", foreign_keys="Local.owner_id")
    api_keys = relationship("APIKey", back_populates="user")
    otp_codes = relationship("OTPCode", back_populates="user")


class Vendor(Base):
    """External service providers (technicians, companies)"""
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(50), unique=True)  # RUT in Chile
    contact_email = Column(String(255))
    phone_number = Column(String(50))
    vendor_type = Column(String(50))  # "independent", "company"
    bank_details = Column(JSON)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="vendor")


# Add vendor relationship to User
User.vendor = relationship("Vendor", back_populates="users")


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
    tax_id = Column(String(50))  # RUT del local
    
    # Visual & Documents
    floor_plan_url = Column(String(500))
    
    # Billing
    billing_address = Column(Text)
    cost_center_code = Column(String(50))
    tax_rate_override = Column(Float)  # Override default tax rate
    
    # Geofencing
    geofence_polygon = Column(JSON)  # GeoJSON polygon
    
    # Timestamps & Versioning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    row_version = Column(Integer, default=1)  # For sync conflict resolution
    
    # Relationships
    owner = relationship("User", back_populates="owned_locales", foreign_keys=[owner_id])
    areas = relationship("LocalArea", back_populates="local")
    members = relationship("LocalMember", back_populates="local")


class LocalArea(Base):
    """Subdivisions within a location (floors, rooms, zones)"""
    __tablename__ = "local_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    floor_plan_url = Column(String(500))
    
    # Booking
    is_bookable = Column(Boolean, default=False)
    capacity_people = Column(Integer)
    
    # Risk & Access
    criticality = Column(String(50))  # "low", "standard", "high", "mission_critical"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    row_version = Column(Integer, default=1)
    
    # Relationships
    local = relationship("Local", back_populates="areas")


class LocalMember(Base):
    """Users with access to a specific location"""
    __tablename__ = "local_members"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(SQLEnum(UserRole), nullable=False)
    permissions = Column(JSON, default=[])  # Granular permissions
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    local = relationship("Local", back_populates="members")
    user = relationship("User")


# ============================================================================
# API KEYS & OTP
# ============================================================================

class APIKey(Base):
    """API keys for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    key_name = Column(String(100), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    scopes = Column(JSON, default=[])  # List of allowed operations
    
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class OTPCode(Base):
    """One-time passwords for email/SMS verification"""
    __tablename__ = "otp_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)  # "email_verification", "password_reset", "2fa"
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="otp_codes")


class IdentityProvider(Base):
    """SSO configuration (Azure AD, Google, Okta, etc.)"""
    __tablename__ = "identity_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    provider_type = Column(String(50), nullable=False)  # "azure_ad", "google_workspace", etc.
    domain = Column(String(255), nullable=False)  # Email domain to match
    
    # OAuth2 Config
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(500), nullable=False)
    issuer_url = Column(String(500), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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
    user_agent = Column(String(500))
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ============================================================================
# STEP 2: ASSETS & PHYSICAL LAYER
# ============================================================================

class Asset(Base):
    """Physical assets (equipment, machinery, infrastructure)"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("local_areas.id"), nullable=True)
    parent_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # For nested assets
    
    # Basic Info
    name = Column(String(255), nullable=False)
    qr_code = Column(String(100), unique=True, index=True)
    brand = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    category = Column(SQLEnum(ProductCategory), nullable=False)
    image_url = Column(String(500))
    
    # Status & Documentation
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.OPERATIONAL)
    manual_pdf_url = Column(String(500))
    warranty_pdf_url = Column(String(500))
    
    # Dates
    installation_date = Column(DateTime(timezone=True))
    warranty_expiry = Column(DateTime(timezone=True))
    last_maintenance_date = Column(DateTime(timezone=True))
    
    # Meter Reading (for usage-based maintenance)
    last_meter_reading = Column(Float)
    meter_unit = Column(String(50))  # "hours", "km", "cycles"
    
    # Financial
    purchase_price = Column(Float)
    residual_value = Column(Float)
    
    # Map Position (for floor plan visualization)
    map_position_x = Column(Float)
    map_position_y = Column(Float)
    
    # Timestamps & Versioning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    row_version = Column(Integer, default=1)
    
    # Relationships
    local = relationship("Local")
    area = relationship("LocalArea")
    parent_asset = relationship("Asset", remote_side=[id])
    bom_items = relationship("AssetBOM", back_populates="asset")
    maintenance_plans = relationship("AssetMaintenancePlan", back_populates="asset")
    iot_devices = relationship("IoTDevice", back_populates="asset")


class AssetBOM(Base):
    """Bill of Materials - Parts required for asset"""
    __tablename__ = "asset_bom"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Now properly linked
    
    quantity_required = Column(Integer, nullable=False)
    criticality = Column(String(50))  # "critical", "recommended", "optional"
    
    # Relationships
    asset = relationship("Asset", back_populates="bom_items")
    product = relationship("Product")


class AssetMaintenancePlan(Base):
    """Scheduled maintenance plans for assets"""
    __tablename__ = "asset_maintenance_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # "date_based", "meter_based"
    
    # Date-based triggers
    frequency_days = Column(Integer)
    next_due_date = Column(DateTime(timezone=True))
    
    # Meter-based triggers
    frequency_meter = Column(Float)  # Every X hours/km/cycles
    next_due_meter = Column(Float)
    
    # Protocol reference (will be defined in future step)
    protocol_id = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_plans")


# ============================================================================
# IOT & TELEMETRY
# ============================================================================

class IoTDevice(Base):
    """IoT sensors and devices attached to assets"""
    __tablename__ = "iot_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    device_type = Column(String(100), nullable=False)  # "temperature", "vibration", "energy"
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="iot_devices")


# ============================================================================
# WORKFLOWS & OPERATIONS
# ============================================================================

class Workflow(Base):
    """Custom workflow definitions for ticket status transitions"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow")


class WorkflowStep(Base):
    """Individual steps in a workflow"""
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    
    from_status = Column(SQLEnum(TicketStatus), nullable=False)
    to_status = Column(SQLEnum(TicketStatus), nullable=False)
    required_role = Column(SQLEnum(UserRole), nullable=True)  # Who can perform this transition
    required_form_template_id = Column(Integer, nullable=True)  # Form to fill before transition
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")


# ============================================================================
# SERVICE TICKETS (CORE OPERATIONS)
# ============================================================================

class ServiceTicket(Base):
    """Service tickets - the heart of operations"""
    __tablename__ = "service_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    
    # Ticket Info
    ticket_type = Column(String(50))  # "corrective", "preventive", "inspection"
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    description = Column(Text, nullable=False)
    
    # SLA
    sla_deadline = Column(DateTime(timezone=True))
    
    # AI Diagnosis
    ai_diagnosis = Column(Text)
    
    # Work Dates
    visit_date = Column(DateTime(timezone=True))
    work_started_at = Column(DateTime(timezone=True))
    work_ended_at = Column(DateTime(timezone=True))
    
    # Completion
    technician_notes = Column(Text)
    customer_signature_url = Column(String(500))
    signed_at = Column(DateTime(timezone=True))
    
    # Financial
    quoted_price = Column(Float)
    provider_cost = Column(Float)  # Cost to pay technician/vendor
    
    # Timestamps & Versioning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    row_version = Column(Integer, default=1)
    
    # Relationships
    local = relationship("Local")
    requester = relationship("User", foreign_keys=[requester_id])
    assigned_technician = relationship("User", foreign_keys=[assigned_technician_id])
    asset = relationship("Asset")
    workflow = relationship("Workflow")
    tasks = relationship("TicketTask", back_populates="ticket")
    attachments = relationship("TicketAttachment", back_populates="ticket")


class TicketTask(Base):
    """Checklist items within a ticket"""
    __tablename__ = "ticket_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=False)
    
    description = Column(String(500), nullable=False)
    is_done = Column(Boolean, default=False)
    required_photo = Column(Boolean, default=False)
    
    row_version = Column(Integer, default=1)
    
    # Relationships
    ticket = relationship("ServiceTicket", back_populates="tasks")


class TicketAttachment(Base):
    """Photos, videos, documents attached to tickets"""
    __tablename__ = "ticket_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=False)
    
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50))  # "photo", "video", "pdf"
    description = Column(String(500))
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("ServiceTicket", back_populates="attachments")


# ============================================================================
# WORKFORCE MANAGEMENT
# ============================================================================

class TechnicianShift(Base):
    """Technician work schedules"""
    __tablename__ = "technician_shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    shift_type = Column(SQLEnum(ShiftType), default=ShiftType.WORKING)
    
    is_approved = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")


class TechnicianCertification(Base):
    """Legal certifications and licenses"""
    __tablename__ = "technician_certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)  # e.g., "SEC Clase A"
    document_url = Column(String(500))
    expiry_date = Column(DateTime(timezone=True))
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


# ============================================================================
# STEP 3: SUPPLY CHAIN - WAREHOUSES & PRODUCTS
# ============================================================================

class Warehouse(Base):
    """Storage locations for inventory"""
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    warehouse_type = Column(String(50), nullable=False)  # "central", "mobile_van", "client_site"
    address = Column(Text)
    responsible_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    responsible = relationship("User", foreign_keys=[responsible_user_id])
    stocks = relationship("InventoryStock", back_populates="warehouse")


class Product(Base):
    """Product/Service catalog"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(ProductCategory), nullable=False)
    sku = Column(String(100), unique=True, index=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="CLP")
    
    # Media
    image_url = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    vendors = relationship("ProductVendor", back_populates="product")
    stocks = relationship("InventoryStock", back_populates="product")


class ProductVendor(Base):
    """Multi-vendor pricing for products"""
    __tablename__ = "product_vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    vendor_sku = Column(String(100))  # Vendor's SKU for this product
    unit_price = Column(Float, nullable=False)
    currency = Column(String(10), default="CLP")
    lead_time_days = Column(Integer)  # Delivery time
    is_preferred = Column(Boolean, default=False)  # Preferred vendor for this product
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="vendors")
    vendor = relationship("Vendor")


class InventoryStock(Base):
    """Real-time stock levels per warehouse"""
    __tablename__ = "inventory_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Current Stock
    quantity = Column(Float, nullable=False, default=0)
    
    # Auto-Replenishment
    min_stock = Column(Float)  # Minimum stock level
    max_stock = Column(Float)  # Maximum stock level
    reorder_point = Column(Float)  # Trigger reorder when stock falls below this
    auto_replenish = Column(Boolean, default=False)  # Auto-create requisition
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="stocks")
    product = relationship("Product", back_populates="stocks")


class InventoryMovement(Base):
    """Kardex - Inventory transaction log"""
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Movement Direction
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    
    quantity = Column(Float, nullable=False)
    movement_type = Column(SQLEnum(MovementType), nullable=False)
    
    # Reference
    reference_ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    product = relationship("Product")
    from_warehouse = relationship("Warehouse", foreign_keys=[from_warehouse_id])
    to_warehouse = relationship("Warehouse", foreign_keys=[to_warehouse_id])
    ticket = relationship("ServiceTicket")
    user = relationship("User")


# ============================================================================
# PROCUREMENT - PURCHASE REQUISITIONS & ORDERS
# ============================================================================

class PurchaseRequisition(Base):
    """Internal purchase request"""
    __tablename__ = "purchase_requisitions"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(SQLEnum(RequisitionStatus), default=RequisitionStatus.DRAFT)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    requester = relationship("User")
    items = relationship("RequisitionItem", back_populates="requisition")


class RequisitionItem(Base):
    """Line items in a purchase requisition"""
    __tablename__ = "requisition_items"
    
    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey("purchase_requisitions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity_requested = Column(Float, nullable=False)
    
    # Relationships
    requisition = relationship("PurchaseRequisition", back_populates="items")
    product = relationship("Product")


class PurchaseOrder(Base):
    """Legal purchase order to vendor"""
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    requisition_id = Column(Integer, ForeignKey("purchase_requisitions.id"), nullable=True)
    
    po_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(POStatus), default=POStatus.DRAFT)
    
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="CLP")
    
    pdf_url = Column(String(500))  # Generated PO document
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    vendor = relationship("Vendor")
    requisition = relationship("PurchaseRequisition")
    approver = relationship("User", foreign_keys=[approved_by])
    items = relationship("POItem", back_populates="purchase_order")


class POItem(Base):
    """Line items in a purchase order"""
    __tablename__ = "po_items"
    
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity_ordered = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity_received = Column(Float, default=0)  # Track partial receipts
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")


class GoodsReceipt(Base):
    """Warehouse receipt of goods (GRN)"""
    __tablename__ = "goods_receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    
    received_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    delivery_note_number = Column(String(100))  # Guía de despacho
    
    # Relationships
    purchase_order = relationship("PurchaseOrder")
    warehouse = relationship("Warehouse")
    receiver = relationship("User")


# ============================================================================
# FINANCIAL MANAGEMENT
# ============================================================================

class BudgetCenter(Base):
    """Cost centers for budget control"""
    __tablename__ = "budget_centers"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    code = Column(String(50), nullable=False, index=True)  # CC code
    name = Column(String(255), nullable=False)
    
    budget_limit_amount = Column(Float, nullable=False)
    current_spend_amount = Column(Float, default=0)
    currency = Column(String(10), default="CLP")
    
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")


class ClientContract(Base):
    """Client contracts with price adjustments (CLM)"""
    __tablename__ = "client_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Client/Tenant
    
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    monthly_value = Column(Float, nullable=False)
    currency = Column(String(10), default="CLP")
    
    # Price Adjustment
    adjustment_index = Column(SQLEnum(AdjustmentIndex), default=AdjustmentIndex.NONE)
    next_adjustment_date = Column(DateTime(timezone=True))
    
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)
    document_url = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    client = relationship("User", foreign_keys=[client_id])


class BillingBatch(Base):
    """Batch invoicing for multiple tickets"""
    __tablename__ = "billing_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    batch_name = Column(String(255), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    invoice_pdf_url = Column(String(500))
    sii_folio = Column(String(100))  # Chilean tax folio number
    
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    client = relationship("User", foreign_keys=[client_id])


class TicketPenalty(Base):
    """SLA penalties for late ticket completion"""
    __tablename__ = "ticket_penalties"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=False)
    sla_rule_id = Column(Integer, nullable=True)  # Reference to SLA policy (future step)
    
    delay_minutes = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="CLP")
    is_contested = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("ServiceTicket")


# ============================================================================
# STEP 4: SAFETY & INDUSTRIAL SECURITY (HSE - ISO 45001)
# ============================================================================

class RiskMatrix(Base):
    """Risk assessment matrix configuration"""
    __tablename__ = "risk_matrices"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)  # e.g., "5x5 Matrix"
    severity_levels = Column(JSON, nullable=False)  # ["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"]
    probability_levels = Column(JSON, nullable=False)  # ["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")


class LotoProcedure(Base):
    """Lock-Out Tag-Out procedures for assets"""
    __tablename__ = "loto_procedures"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    procedure_steps = Column(Text, nullable=False)
    required_locks = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset")


class LotoLog(Base):
    """LOTO application/removal evidence"""
    __tablename__ = "loto_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    action = Column(SQLEnum(LotoStatus), nullable=False)  # applied or removed
    photo_url = Column(String(500))  # Evidence photo
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("ServiceTicket")
    asset = relationship("Asset")
    user = relationship("User")


class WorkPermit(Base):
    """Work permits with risk assessment (CRITICAL for safety)"""
    __tablename__ = "work_permits"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=False)
    risk_matrix_id = Column(Integer, ForeignKey("risk_matrices.id"), nullable=True)
    
    risk_assessment = Column(Text, nullable=False)
    calculated_risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    
    supervisor_signature_url = Column(String(500))
    technician_signature_url = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    
    # Relationships
    ticket = relationship("ServiceTicket")
    risk_matrix = relationship("RiskMatrix")


# ============================================================================
# TRAINING & LEARNING MANAGEMENT (LMS)
# ============================================================================

class TrainingModule(Base):
    """Training courses and materials"""
    __tablename__ = "training_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_url = Column(String(500))  # Video, PDF, SCORM package
    
    min_score_to_pass = Column(Integer, default=70)  # Percentage
    duration_minutes = Column(Integer)
    
    # Compliance: Required for specific asset categories
    required_for_asset_category = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")
    quizzes = relationship("TrainingQuiz", back_populates="module")
    progress_records = relationship("UserTrainingProgress", back_populates="module")


class TrainingQuiz(Base):
    """Quizzes for training modules"""
    __tablename__ = "training_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False)
    
    questions_json = Column(JSON, nullable=False)  # Array of questions with answers
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    module = relationship("TrainingModule", back_populates="quizzes")


class UserTrainingProgress(Base):
    """User training completion tracking"""
    __tablename__ = "user_training_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False)
    
    status = Column(SQLEnum(TrainingStatus), default=TrainingStatus.ASSIGNED)
    score = Column(Integer, nullable=True)  # Quiz score percentage
    
    completed_at = Column(DateTime(timezone=True), nullable=True)
    certificate_url = Column(String(500), nullable=True)  # Generated certificate
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    module = relationship("TrainingModule", back_populates="progress_records")


# ============================================================================
# VISITOR MANAGEMENT SYSTEM (VMS)
# ============================================================================

class VisitorInvite(Base):
    """Visitor invitations with QR codes"""
    __tablename__ = "visitor_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    visitor_name = Column(String(255), nullable=False)
    visitor_rut = Column(String(50))  # Chilean ID
    visitor_email = Column(String(255))
    
    qr_token = Column(String(255), unique=True, nullable=False, index=True)
    expected_arrival = Column(DateTime(timezone=True), nullable=False)
    
    status = Column(SQLEnum(VisitorStatus), default=VisitorStatus.INVITED)
    nda_signed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    local = relationship("Local")
    inviter = relationship("User")
    ndas = relationship("VisitorNDA", back_populates="invite")


class VisitorNDA(Base):
    """Non-Disclosure Agreements for visitors"""
    __tablename__ = "visitor_ndas"
    
    id = Column(Integer, primary_key=True, index=True)
    visitor_invite_id = Column(Integer, ForeignKey("visitor_invites.id"), nullable=False)
    
    document_url = Column(String(500), nullable=False)  # Signed PDF
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invite = relationship("VisitorInvite", back_populates="ndas")


class AccessLog(Base):
    """Security gate access log (guard station)"""
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    guard_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Link to visitor invite (if pre-registered)
    visitor_invite_id = Column(Integer, ForeignKey("visitor_invites.id"), nullable=True)
    
    # Manual entry fields
    visitor_name = Column(String(255), nullable=False)
    visitor_rut = Column(String(50))
    access_type = Column(SQLEnum(AccessType), nullable=False)
    
    # Ticket reference (for contractors/technicians)
    related_ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=True)
    
    check_in_time = Column(DateTime(timezone=True), server_default=func.now())
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    vehicle_plate = Column(String(50))
    
    # Relationships
    local = relationship("Local")
    guard = relationship("User")
    visitor_invite = relationship("VisitorInvite")
    ticket = relationship("ServiceTicket")


class ShiftHandover(Base):
    """Guard/technician shift handover log"""
    __tablename__ = "shift_handovers"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    outgoing_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    incoming_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    handover_notes = Column(Text, nullable=False)
    critical_alerts_pending = Column(Integer, default=0)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    local = relationship("Local")
    outgoing_user = relationship("User", foreign_keys=[outgoing_user_id])
    incoming_user = relationship("User", foreign_keys=[incoming_user_id])


# ============================================================================
# QUALITY & ESG (SUSTAINABILITY)
# ============================================================================

class QualityAudit(Base):
    """Quality audits and inspections"""
    __tablename__ = "quality_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    auditor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    form_template_id = Column(Integer, nullable=True)  # Reference to form (future)
    
    score_obtained = Column(Float, nullable=False)
    score_max = Column(Float, nullable=False)
    compliance_percentage = Column(Float, nullable=False)
    
    audit_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="completed")
    
    # Relationships
    local = relationship("Local")
    auditor = relationship("User")


class EmissionFactor(Base):
    """Carbon footprint emission factors"""
    __tablename__ = "emission_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    resource_name = Column(String(255), nullable=False)  # "Electricity", "Diesel", etc.
    unit = Column(String(50), nullable=False)  # "kWh", "liters"
    co2_factor = Column(Float, nullable=False)  # kg CO2 per unit
    emission_scope = Column(SQLEnum(EmissionScope), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")


class SustainabilityGoal(Base):
    """ESG sustainability targets"""
    __tablename__ = "sustainability_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    year = Column(Integer, nullable=False)
    target_reduction_percentage = Column(Float, nullable=False)  # % reduction vs baseline
    baseline_year = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")


# ============================================================================
# READY FOR STEP 5
# ============================================================================
# Next steps will add:
# - Step 5: Advanced Features (BIM, Incidents, Analytics, Reports, SLA Policies)

# ============================================================================
# STEP 5: BIM & DIGITAL TWIN (ISO 19650)
# ============================================================================

class BIMModel(Base):
    """BIM/3D models for facilities"""
    __tablename__ = "bim_models"
    
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    model_file_url = Column(String(500), nullable=False)
    viewer_urn = Column(String(500))  # Autodesk Forge URN
    format = Column(SQLEnum(BIMFormat), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    local = relationship("Local")
    object_mappings = relationship("BIMObjectMapping", back_populates="bim_model")


class BIMObjectMapping(Base):
    """Link BIM objects to physical assets"""
    __tablename__ = "bim_object_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    bim_model_id = Column(Integer, ForeignKey("bim_models.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    object_guid = Column(String(255), nullable=False)  # Unique ID in 3D model
    
    # Relationships
    bim_model = relationship("BIMModel", back_populates="object_mappings")
    asset = relationship("Asset")


# ============================================================================
# AI & STRUCTURED DATA (RCM - Reliability Centered Maintenance)
# ============================================================================

class FailureHierarchy(Base):
    """Failure code hierarchies for RCM"""
    __tablename__ = "failure_hierarchies"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    asset_category = Column(String(100))  # Applicable to which asset type
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")
    codes = relationship("FailureCode", back_populates="hierarchy")


class FailureCode(Base):
    """Structured failure codes (Problem/Cause/Remedy)"""
    __tablename__ = "failure_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    hierarchy_id = Column(Integer, ForeignKey("failure_hierarchies.id"), nullable=False)
    parent_code_id = Column(Integer, ForeignKey("failure_codes.id"), nullable=True)
    
    code = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    code_type = Column(SQLEnum(FailureCodeType), nullable=False)
    
    # Relationships
    hierarchy = relationship("FailureHierarchy", back_populates="codes")
    parent = relationship("FailureCode", remote_side=[id])


class TicketFailureReport(Base):
    """Structured failure reporting for AI training"""
    __tablename__ = "ticket_failure_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("service_tickets.id"), nullable=False)
    
    problem_code_id = Column(Integer, ForeignKey("failure_codes.id"), nullable=False)
    cause_code_id = Column(Integer, ForeignKey("failure_codes.id"), nullable=False)
    remedy_code_id = Column(Integer, ForeignKey("failure_codes.id"), nullable=False)
    
    comments = Column(Text)
    
    # Relationships
    ticket = relationship("ServiceTicket")
    problem_code = relationship("FailureCode", foreign_keys=[problem_code_id])
    cause_code = relationship("FailureCode", foreign_keys=[cause_code_id])
    remedy_code = relationship("FailureCode", foreign_keys=[remedy_code_id])


class AssetHealthHistory(Base):
    """AI-generated asset health predictions (time series)"""
    __tablename__ = "asset_health_history"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    health_score = Column(Float, nullable=False)  # 0-100
    
    predicted_failure_date = Column(DateTime(timezone=True))
    prediction_confidence = Column(Float)  # 0-1
    contributing_factors = Column(JSON)  # {"vibration": 0.8, "temperature": 0.6}
    
    # Relationships
    asset = relationship("Asset")


class AssetDepreciationSchedule(Base):
    """Asset depreciation for financial reporting"""
    __tablename__ = "asset_depreciation_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    method = Column(SQLEnum(DepreciationMethod), nullable=False)
    useful_life_years = Column(Integer, nullable=False)
    current_book_value = Column(Float, nullable=False)
    
    last_calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset")


# ============================================================================
# UX & MOBILE SYNC
# ============================================================================

class UserDevice(Base):
    """Mobile device management (MDM Lite)"""
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    device_uuid = Column(String(255), unique=True, nullable=False, index=True)
    device_name = Column(String(255))
    os_version = Column(String(50))
    app_version = Column(String(50))
    
    last_sync_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    sync_cursors = relationship("SyncCursor", back_populates="device")


class SyncCursor(Base):
    """Delta sync tracking per table"""
    __tablename__ = "sync_cursors"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("user_devices.id"), nullable=False)
    
    table_name = Column(String(100), nullable=False)
    last_row_version = Column(Integer, nullable=False)  # Last synced row_version
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    device = relationship("UserDevice", back_populates="sync_cursors")


class DashboardLayout(Base):
    """User-customizable dashboard layouts"""
    __tablename__ = "dashboard_layouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    widgets = relationship("DashboardWidget", back_populates="layout")


class DashboardWidget(Base):
    """Dashboard widget configuration"""
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    layout_id = Column(Integer, ForeignKey("dashboard_layouts.id"), nullable=False)
    
    widget_type = Column(SQLEnum(WidgetType), nullable=False)
    data_source = Column(String(100))  # "tickets", "assets", "sensors"
    
    # Grid position
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    config_json = Column(JSON)  # Widget-specific config
    
    # Relationships
    layout = relationship("DashboardLayout", back_populates="widgets")


class I18nContent(Base):
    """Dynamic translations for multi-language support"""
    __tablename__ = "i18n_content"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    language_code = Column(String(10), nullable=False)  # "es", "en", "pt"
    field_name = Column(String(100), nullable=False)
    translated_value = Column(Text, nullable=False)
    
    # Relationships
    owner = relationship("User")


# ============================================================================
# SYSTEM & REPORTING
# ============================================================================

class GeneratedReport(Base):
    """Immutable generated reports with data snapshots"""
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    report_type = Column(SQLEnum(ReportType), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    data_snapshot = Column(JSON, nullable=False)  # Immutable data at generation time
    pdf_url = Column(String(500))
    
    is_final = Column(Boolean, default=False)  # Locked report
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")


class NotificationTemplate(Base):
    """Customizable notification templates per tenant"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    event_type = Column(String(100), nullable=False)  # "ticket_assigned", "alert_critical"
    channel = Column(String(50), nullable=False)  # "email", "push", "sms"
    
    subject_template = Column(String(500))
    body_template = Column(Text, nullable=False)  # HTML with {{variables}}
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")


class DataRetentionPolicy(Base):
    """Automated data cleanup policies"""
    __tablename__ = "data_retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    table_name = Column(String(100), nullable=False, unique=True)
    retention_days = Column(Integer, nullable=False)
    strategy = Column(SQLEnum(RetentionStrategy), nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UsageRecord(Base):
    """Metered usage for variable billing"""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    metric = Column(String(100), nullable=False)  # "api_calls", "storage_gb", "ai_predictions"
    quantity = Column(Float, nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    billing_period = Column(String(20), nullable=False)  # "2025-01"
    
    # Relationships
    owner = relationship("User")


# ============================================================================
# V62 ENTERPRISE MASTER - COMPLETE
# ============================================================================
# Total Tables: 65+
# Total Enums: 26
# This schema represents a complete enterprise facility management platform
# with IoT, AI, BIM, compliance, and multi-tenant capabilities.
