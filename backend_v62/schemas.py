"""
Pydantic Schemas for V62 - Complete (Steps 1-5)
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from sql_models import (
    # Step 1 & 2
    UserRole, PlanType,
    AssetStatus, ProductCategory, TicketStatus, TicketPriority,
    TechnicianSkill, ShiftType,
    # Step 3
    PaymentStatus, RequisitionStatus, POStatus, ContractStatus,
    MovementType, AdjustmentIndex,
    # Step 4
    RiskLevel, LotoStatus, TrainingStatus, VisitorStatus,
    AccessType, EmissionScope,
    # Step 5
    BIMFormat, ReportType, WidgetType, FailureCodeType,
    RetentionStrategy, DepreciationMethod
)


# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    is_public: bool = False


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSetting(SystemSettingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PLAN LIMITS
# ============================================================================

class PlanLimitBase(BaseModel):
    plan_type: PlanType
    resource: str
    limit_value: int
    overage_price: Optional[float] = None


class PlanLimitCreate(PlanLimitBase):
    pass


class PlanLimit(PlanLimitBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# USERS
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.STAFF


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    fcm_token: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    profile_image_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    technician_skills: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    """User model with hashed password (internal use only)"""
    hashed_password: Optional[str] = None


# ============================================================================
# AUTHENTICATION
# ============================================================================

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: User


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    user_id: int
    email: str
    role: UserRole


class LoginRequest(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    """Registration with additional fields"""
    company_name: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with OTP"""
    email: EmailStr
    otp_code: str
    new_password: str = Field(..., min_length=8)


class OTPVerifyRequest(BaseModel):
    """Verify OTP code"""
    email: EmailStr
    code: str
    purpose: str  # "email_verification", "password_reset", "2fa"


# ============================================================================
# LOCALES (LOCATIONS)
# ============================================================================

class LocalBase(BaseModel):
    name: str
    address: str
    tax_id: Optional[str] = None
    floor_plan_url: Optional[str] = None
    billing_address: Optional[str] = None


class LocalCreate(LocalBase):
    pass


class LocalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    floor_plan_url: Optional[str] = None
    billing_address: Optional[str] = None
    geofence_polygon: Optional[Dict[str, Any]] = None


class Local(LocalBase):
    id: int
    owner_id: int
    cost_center_code: Optional[str] = None
    tax_rate_override: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    row_version: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LOCAL AREAS
# ============================================================================

class LocalAreaBase(BaseModel):
    name: str
    is_bookable: bool = False
    capacity_people: Optional[int] = None
    criticality: str = "standard"


class LocalAreaCreate(LocalAreaBase):
    local_id: int


class LocalArea(LocalAreaBase):
    id: int
    local_id: int
    floor_plan_url: Optional[str] = None
    created_at: datetime
    row_version: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LOCAL MEMBERS
# ============================================================================

class LocalMemberBase(BaseModel):
    user_id: int
    role: UserRole
    permissions: List[str] = []


class LocalMemberCreate(LocalMemberBase):
    local_id: int


class LocalMember(LocalMemberBase):
    id: int
    local_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# API KEYS
# ============================================================================

class APIKeyBase(BaseModel):
    key_name: str
    scopes: List[str] = []
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKey(APIKeyBase):
    id: int
    api_key: str  # Only returned on creation
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class APIKeyList(BaseModel):
    """API key without the actual key (for listing)"""
    id: int
    key_name: str
    scopes: List[str]
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# AUDIT LOGS
# ============================================================================

class AuditLog(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    table_name: str
    record_id: Optional[int] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# COMMON RESPONSES
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
# ============================================================================
# STEP 2: ASSETS
# ============================================================================

class AssetBase(BaseModel):
    name: str
    category: ProductCategory
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.OPERATIONAL


class AssetCreate(AssetBase):
    local_id: int
    area_id: Optional[int] = None
    parent_asset_id: Optional[int] = None
    qr_code: Optional[str] = None
    installation_date: Optional[datetime] = None
    purchase_price: Optional[float] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[AssetStatus] = None
    area_id: Optional[int] = None
    image_url: Optional[str] = None
    last_maintenance_date: Optional[datetime] = None
    last_meter_reading: Optional[float] = None


class Asset(AssetBase):
    id: int
    local_id: int
    area_id: Optional[int] = None
    parent_asset_id: Optional[int] = None
    qr_code: Optional[str] = None
    image_url: Optional[str] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    row_version: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ASSET MAINTENANCE PLANS
# ============================================================================

class AssetMaintenancePlanBase(BaseModel):
    name: str
    trigger_type: str  # "date_based" or "meter_based"
    frequency_days: Optional[int] = None
    frequency_meter: Optional[float] = None


class AssetMaintenancePlanCreate(AssetMaintenancePlanBase):
    asset_id: int


class AssetMaintenancePlan(AssetMaintenancePlanBase):
    id: int
    asset_id: int
    next_due_date: Optional[datetime] = None
    next_due_meter: Optional[float] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# IOT DEVICES
# ============================================================================

class IoTDeviceBase(BaseModel):
    device_type: str
    is_online: bool = False


class IoTDeviceCreate(IoTDeviceBase):
    asset_id: int


class IoTDevice(IoTDeviceBase):
    id: int
    asset_id: int
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# WORKFLOWS
# ============================================================================

class WorkflowBase(BaseModel):
    name: str
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    pass


class Workflow(WorkflowBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowStepBase(BaseModel):
    from_status: TicketStatus
    to_status: TicketStatus
    required_role: Optional[UserRole] = None


class WorkflowStepCreate(WorkflowStepBase):
    workflow_id: int


class WorkflowStep(WorkflowStepBase):
    id: int
    workflow_id: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SERVICE TICKETS
# ============================================================================

class ServiceTicketBase(BaseModel):
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    ticket_type: Optional[str] = "corrective"


class ServiceTicketCreate(ServiceTicketBase):
    local_id: int
    asset_id: Optional[int] = None
    visit_date: Optional[datetime] = None


class ServiceTicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    assigned_technician_id: Optional[int] = None
    priority: Optional[TicketPriority] = None
    visit_date: Optional[datetime] = None
    work_started_at: Optional[datetime] = None
    work_ended_at: Optional[datetime] = None
    technician_notes: Optional[str] = None
    customer_signature_url: Optional[str] = None
    quoted_price: Optional[float] = None


class ServiceTicket(ServiceTicketBase):
    id: int
    local_id: int
    requester_id: int
    assigned_technician_id: Optional[int] = None
    asset_id: Optional[int] = None
    status: TicketStatus
    ai_diagnosis: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    visit_date: Optional[datetime] = None
    work_started_at: Optional[datetime] = None
    work_ended_at: Optional[datetime] = None
    technician_notes: Optional[str] = None
    quoted_price: Optional[float] = None
    provider_cost: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    row_version: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TICKET TASKS
# ============================================================================

class TicketTaskBase(BaseModel):
    description: str
    required_photo: bool = False


class TicketTaskCreate(TicketTaskBase):
    ticket_id: int


class TicketTaskUpdate(BaseModel):
    is_done: Optional[bool] = None


class TicketTask(TicketTaskBase):
    id: int
    ticket_id: int
    is_done: bool
    row_version: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TICKET ATTACHMENTS
# ============================================================================

class TicketAttachmentBase(BaseModel):
    file_url: str
    file_type: str  # "photo", "video", "pdf"
    description: Optional[str] = None


class TicketAttachmentCreate(TicketAttachmentBase):
    ticket_id: int


class TicketAttachment(TicketAttachmentBase):
    id: int
    ticket_id: int
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TECHNICIAN SHIFTS
# ============================================================================

class TechnicianShiftBase(BaseModel):
    start_time: datetime
    end_time: datetime
    shift_type: ShiftType = ShiftType.WORKING


class TechnicianShiftCreate(TechnicianShiftBase):
    user_id: int


class TechnicianShift(TechnicianShiftBase):
    id: int
    user_id: int
    is_approved: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TECHNICIAN CERTIFICATIONS
# ============================================================================

class TechnicianCertificationBase(BaseModel):
    name: str
    document_url: Optional[str] = None
    expiry_date: Optional[datetime] = None


class TechnicianCertificationCreate(TechnicianCertificationBase):
    user_id: int


class TechnicianCertification(TechnicianCertificationBase):
    id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# STEP 3: WAREHOUSES & PRODUCTS
# ============================================================================

class WarehouseBase(BaseModel):
    name: str
    warehouse_type: str  # "central", "mobile_van", "client_site"
    address: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    responsible_user_id: Optional[int] = None


class Warehouse(WarehouseBase):
    id: int
    owner_id: int
    responsible_user_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    category: ProductCategory
    sku: str
    price: float
    currency: str = "CLP"
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductVendorBase(BaseModel):
    vendor_sku: Optional[str] = None
    unit_price: float
    currency: str = "CLP"
    lead_time_days: Optional[int] = None
    is_preferred: bool = False


class ProductVendorCreate(ProductVendorBase):
    product_id: int
    vendor_id: int


class ProductVendor(ProductVendorBase):
    id: int
    product_id: int
    vendor_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

class InventoryStockBase(BaseModel):
    quantity: float = 0
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    reorder_point: Optional[float] = None
    auto_replenish: bool = False


class InventoryStockCreate(InventoryStockBase):
    warehouse_id: int
    product_id: int


class InventoryStockUpdate(BaseModel):
    quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    reorder_point: Optional[float] = None


class InventoryStock(InventoryStockBase):
    id: int
    warehouse_id: int
    product_id: int
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InventoryMovementBase(BaseModel):
    quantity: float
    movement_type: MovementType


class InventoryMovementCreate(InventoryMovementBase):
    product_id: int
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    reference_ticket_id: Optional[int] = None


class InventoryMovement(InventoryMovementBase):
    id: int
    product_id: int
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    reference_ticket_id: Optional[int] = None
    performed_by: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PROCUREMENT
# ============================================================================

class PurchaseRequisitionBase(BaseModel):
    notes: Optional[str] = None


class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    pass


class PurchaseRequisition(PurchaseRequisitionBase):
    id: int
    requester_id: int
    status: RequisitionStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RequisitionItemBase(BaseModel):
    quantity_requested: float


class RequisitionItemCreate(RequisitionItemBase):
    requisition_id: int
    product_id: int


class RequisitionItem(RequisitionItemBase):
    id: int
    requisition_id: int
    product_id: int
    
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderBase(BaseModel):
    po_number: str
    total_amount: float
    currency: str = "CLP"


class PurchaseOrderCreate(PurchaseOrderBase):
    vendor_id: int
    requisition_id: Optional[int] = None


class PurchaseOrderUpdate(BaseModel):
    status: Optional[POStatus] = None
    pdf_url: Optional[str] = None


class PurchaseOrder(PurchaseOrderBase):
    id: int
    owner_id: int
    vendor_id: int
    requisition_id: Optional[int] = None
    status: POStatus
    pdf_url: Optional[str] = None
    approved_by: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class POItemBase(BaseModel):
    quantity_ordered: float
    unit_price: float


class POItemCreate(POItemBase):
    po_id: int
    product_id: int


class POItem(POItemBase):
    id: int
    po_id: int
    product_id: int
    quantity_received: float
    
    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptBase(BaseModel):
    delivery_note_number: Optional[str] = None


class GoodsReceiptCreate(GoodsReceiptBase):
    po_id: int
    warehouse_id: int


class GoodsReceipt(GoodsReceiptBase):
    id: int
    po_id: int
    warehouse_id: int
    received_by: int
    received_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# FINANCIAL MANAGEMENT
# ============================================================================

class BudgetCenterBase(BaseModel):
    code: str
    name: str
    budget_limit_amount: float
    currency: str = "CLP"
    period_start: datetime
    period_end: datetime


class BudgetCenterCreate(BudgetCenterBase):
    pass


class BudgetCenterUpdate(BaseModel):
    budget_limit_amount: Optional[float] = None
    current_spend_amount: Optional[float] = None


class BudgetCenter(BudgetCenterBase):
    id: int
    owner_id: int
    current_spend_amount: float
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ClientContractBase(BaseModel):
    contract_number: str
    title: str
    start_date: datetime
    end_date: datetime
    monthly_value: float
    currency: str = "CLP"
    adjustment_index: AdjustmentIndex = AdjustmentIndex.NONE


class ClientContractCreate(ClientContractBase):
    client_id: int


class ClientContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    end_date: Optional[datetime] = None
    monthly_value: Optional[float] = None
    next_adjustment_date: Optional[datetime] = None


class ClientContract(ClientContractBase):
    id: int
    owner_id: int
    client_id: int
    status: ContractStatus
    next_adjustment_date: Optional[datetime] = None
    document_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BillingBatchBase(BaseModel):
    batch_name: str
    total_amount: float
    period_start: datetime
    period_end: datetime


class BillingBatchCreate(BillingBatchBase):
    client_id: int


class BillingBatch(BillingBatchBase):
    id: int
    owner_id: int
    client_id: int
    status: PaymentStatus
    invoice_pdf_url: Optional[str] = None
    sii_folio: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TicketPenaltyBase(BaseModel):
    delay_minutes: int
    amount: float
    currency: str = "CLP"


class TicketPenaltyCreate(TicketPenaltyBase):
    ticket_id: int
    sla_rule_id: Optional[int] = None


class TicketPenalty(TicketPenaltyBase):
    id: int
    ticket_id: int
    sla_rule_id: Optional[int] = None
    is_contested: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
