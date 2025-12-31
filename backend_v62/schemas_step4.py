
# ============================================================================
# STEP 4: SAFETY & HSE
# ============================================================================

class RiskMatrixBase(BaseModel):
    name: str
    severity_levels: List[str]
    probability_levels: List[str]


class RiskMatrixCreate(RiskMatrixBase):
    pass


class RiskMatrix(RiskMatrixBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LotoProcedureBase(BaseModel):
    procedure_steps: str
    required_locks: int


class LotoProcedureCreate(LotoProcedureBase):
    asset_id: int


class LotoProcedure(LotoProcedureBase):
    id: int
    asset_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkPermitBase(BaseModel):
    risk_assessment: str
    calculated_risk_level: str  # Will use RiskLevel enum


class WorkPermitCreate(WorkPermitBase):
    ticket_id: int
    risk_matrix_id: Optional[int] = None


class WorkPermit(WorkPermitBase):
    id: int
    ticket_id: int
    risk_matrix_id: Optional[int] = None
    supervisor_signature_url: Optional[str] = None
    technician_signature_url: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TRAINING (LMS)
# ============================================================================

class TrainingModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_url: Optional[str] = None
    min_score_to_pass: int = 70
    duration_minutes: Optional[int] = None


class TrainingModuleCreate(TrainingModuleBase):
    required_for_asset_category: Optional[str] = None


class TrainingModule(TrainingModuleBase):
    id: int
    owner_id: int
    required_for_asset_category: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TrainingQuizBase(BaseModel):
    questions_json: Dict[str, Any]


class TrainingQuizCreate(TrainingQuizBase):
    module_id: int


class TrainingQuiz(TrainingQuizBase):
    id: int
    module_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserTrainingProgressBase(BaseModel):
    score: Optional[int] = None


class UserTrainingProgressCreate(UserTrainingProgressBase):
    user_id: int
    module_id: int


class UserTrainingProgressUpdate(BaseModel):
    status: Optional[str] = None  # Will use TrainingStatus enum
    score: Optional[int] = None
    certificate_url: Optional[str] = None


class UserTrainingProgress(UserTrainingProgressBase):
    id: int
    user_id: int
    module_id: int
    status: str  # TrainingStatus enum
    completed_at: Optional[datetime] = None
    certificate_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# VISITORS (VMS)
# ============================================================================

class VisitorInviteBase(BaseModel):
    visitor_name: str
    visitor_rut: Optional[str] = None
    visitor_email: Optional[str] = None
    expected_arrival: datetime


class VisitorInviteCreate(VisitorInviteBase):
    local_id: int


class VisitorInvite(VisitorInviteBase):
    id: int
    local_id: int
    invited_by: int
    qr_token: str
    status: str  # VisitorStatus enum
    nda_signed: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VisitorNDABase(BaseModel):
    document_url: str


class VisitorNDACreate(VisitorNDABase):
    visitor_invite_id: int


class VisitorNDA(VisitorNDABase):
    id: int
    visitor_invite_id: int
    signed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AccessLogBase(BaseModel):
    visitor_name: str
    visitor_rut: Optional[str] = None
    access_type: str  # AccessType enum
    vehicle_plate: Optional[str] = None


class AccessLogCreate(AccessLogBase):
    local_id: int
    visitor_invite_id: Optional[int] = None
    related_ticket_id: Optional[int] = None


class AccessLogUpdate(BaseModel):
    check_out_time: Optional[datetime] = None


class AccessLog(AccessLogBase):
    id: int
    local_id: int
    guard_user_id: int
    visitor_invite_id: Optional[int] = None
    related_ticket_id: Optional[int] = None
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ShiftHandoverBase(BaseModel):
    handover_notes: str
    critical_alerts_pending: int = 0


class ShiftHandoverCreate(ShiftHandoverBase):
    local_id: int
    outgoing_user_id: int
    incoming_user_id: int


class ShiftHandover(ShiftHandoverBase):
    id: int
    local_id: int
    outgoing_user_id: int
    incoming_user_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# QUALITY & ESG
# ============================================================================

class QualityAuditBase(BaseModel):
    score_obtained: float
    score_max: float
    compliance_percentage: float


class QualityAuditCreate(QualityAuditBase):
    local_id: int
    form_template_id: Optional[int] = None


class QualityAudit(QualityAuditBase):
    id: int
    local_id: int
    auditor_id: int
    form_template_id: Optional[int] = None
    audit_date: datetime
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class EmissionFactorBase(BaseModel):
    resource_name: str
    unit: str
    co2_factor: float
    emission_scope: str  # EmissionScope enum


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactor(EmissionFactorBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SustainabilityGoalBase(BaseModel):
    year: int
    target_reduction_percentage: float
    baseline_year: int


class SustainabilityGoalCreate(SustainabilityGoalBase):
    pass


class SustainabilityGoal(SustainabilityGoalBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
