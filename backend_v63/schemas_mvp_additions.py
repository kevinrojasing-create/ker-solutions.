"""
MVP Feature Schemas - Append to schemas.py
New Pydantic models for OCR, AI Diagnosis, Maintenance, Plan Limits, and Health Semaphore
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from sql_models import UrgencyLevel, MaintenanceType, SubscriptionPlan


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
