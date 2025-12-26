from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

# DB Imports
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import sql_models

# Create Tables
sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="KER Solutions API", description="Asset Management & Operational Continuity")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Domain Models (Pydantic) ---

class Asset(BaseModel):
    id: str
    name: str
    category: str
    install_date: datetime
    last_maintenance: datetime
    usage_hours_per_day: float
    maintenance_interval_days: int = 180
    image_url: Optional[str] = None
    
    class Config:
        orm_mode = True

class AssetHealth(BaseModel):
    asset_id: str
    health_score: float
    failure_probability: float
    status: str
    color_code: str

class TriageResult(BaseModel):
    diagnosis: str
    severity: str
    recommended_action: str
    confidence: float

class LegalAlert(BaseModel):
    id: str
    title: str
    due_date: datetime
    days_remaining: int
    severity: str

class TicketCreate(BaseModel):
    asset_id: Optional[str] = None
    description: str
    priority: str  # "Alta", "Media", "Baja"
    image_base64: Optional[str] = None

class Ticket(BaseModel):
    id: int
    asset_id: Optional[str]
    description: str
    priority: str
    status: str
    image_base64: Optional[str]
    created_at: datetime
    ai_diagnosis: Optional[str]
    
    class Config:
        orm_mode = True


# --- Seed Data Logic ---
from sqlalchemy.exc import IntegrityError

# ... (imports)

# ...

# --- Seed Data Logic ---
def seed_data(db: Session):
    if db.query(sql_models.AssetDB).first():
        return # Already seeded
    
    print("Seeding initial data...")
    assets = [
        sql_models.AssetDB(
            id="A001", name="Aire Acondicionado - Salón Principal", category="HVAC",
            install_date=datetime.now() - timedelta(days=700),
            last_maintenance=datetime.now() - timedelta(days=30),
            usage_hours_per_day=10.0
        ),
        sql_models.AssetDB(
            id="A002", name="Extintor - Cocina", category="Seguridad",
            install_date=datetime.now() - timedelta(days=300),
            last_maintenance=datetime.now() - timedelta(days=200),
            usage_hours_per_day=0.0
        ),
        sql_models.AssetDB(
            id="A003", name="Válvula de Gas - Cocina", category="Gas",
            install_date=datetime.now() - timedelta(days=1200),
            last_maintenance=datetime.now() - timedelta(days=400),
            usage_hours_per_day=12.0
        )
    ]
    try:
        db.add_all(assets)
        db.commit()
    except IntegrityError:
        db.rollback()
        print("Data already seeded by another worker (Race Condition handled).")

# ...

# --- Logic: Asset Health Algorithm (The "Heart") ---

def calculate_asset_health(asset: sql_models.AssetDB) -> AssetHealth:
    now = datetime.now()
    age_days = (now - asset.install_date).days
    days_since_maintenance = (now - asset.last_maintenance).days
    
    score = 100.0
    score -= age_days * 0.01
    
    overdue_days = days_since_maintenance - asset.maintenance_interval_days
    if overdue_days > 0:
        score -= overdue_days * 0.5
    else:
        score -= days_since_maintenance * 0.05
        
    usage_factor = asset.usage_hours_per_day / 8.0
    if usage_factor > 1:
        score *= (1 / usage_factor)

    score = max(0.0, min(100.0, score))
    failure_risk = 100.0 - score
    
    if score > 75:
        status = "Óptimo"
        color = "green"
    elif score > 40:
        status = "Advertencia"
        color = "yellow"
    else:
        status = "Riesgo Crítico"
        color = "red"
        
    return AssetHealth(
        asset_id=asset.id,
        health_score=round(score, 1),
        failure_probability=round(failure_risk, 1),
        status=status,
        color_code=color
    )

# --- Endpoints ---

@app.on_event("startup")
def startup_event():
    # Helper to seed data on startup
    db = SessionLocal()
    seed_data(db)
    db.close()

@app.get("/")
def home():
    return {"message": "KER Solutions API Operational (with DB)", "version": "2.0.0"}

@app.get("/assets", response_model=List[Asset])
def get_assets(db: Session = Depends(get_db)):
    return db.query(sql_models.AssetDB).all()

class AssetCreate(BaseModel):
    id: str
    name: str
    category: str
    install_date: datetime
    last_maintenance: datetime
    usage_hours_per_day: float
    maintenance_interval_days: int = 180
    image_url: Optional[str] = None

@app.post("/assets", response_model=Asset, status_code=201)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    # Check if asset ID already exists
    existing = db.query(sql_models.AssetDB).filter(sql_models.AssetDB.id == asset.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Asset with ID {asset.id} already exists")
    
    new_asset = sql_models.AssetDB(**asset.model_dump())
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset


@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = sql_models.TicketDB(
        asset_id=ticket.asset_id,
        description=ticket.description,
        priority=ticket.priority,
        image_base64=ticket.image_base64,
        created_at=datetime.now(),
        status="Pendiente"
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.get("/tickets", response_model=List[Ticket])
def get_tickets(db: Session = Depends(get_db)):
    return db.query(sql_models.TicketDB).all()



@app.get("/assets/{asset_id}/health", response_model=AssetHealth)
def get_asset_health(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(sql_models.AssetDB).filter(sql_models.AssetDB.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return calculate_asset_health(asset)

@app.get("/dashboard/status")
def get_dashboard_status(db: Session = Depends(get_db)):
    """Aggregate health from DB to determine Traffic Light status."""
    assets = db.query(sql_models.AssetDB).all()
    healths = [calculate_asset_health(a) for a in assets]
    
    critical_count = sum(1 for h in healths if h.color_code == "red")
    warning_count = sum(1 for h in healths if h.color_code == "yellow")
    
    if critical_count > 0:
        overall = "red"
        msg = "¡Tienda en Estado Crítico! Acción Inmediata Requerida."
    elif warning_count > 0:
        overall = "yellow"
        msg = "Advertencias detectadas. Programe mantenimiento pronto."
    else:
        overall = "green"
        msg = "Tienda Operativa. Todos los sistemas nominales."
        
    return {
        "overall_color": overall,
        "message": msg,
        "details": healths
    }

@app.post("/triage/analyze", response_model=TriageResult)
async def analyze_failure_image(file: UploadFile = File(...)):
    """
    Real AI Vision Triage using Google Gemini 1.5 Flash.
    Analyzes facility maintenance images and provides expert diagnosis.
    """
    import google.generativeai as genai
    import os
    import base64
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback to mock if no API key
        return TriageResult(
            diagnosis="API Key no configurada - Modo simulación",
            severity="Media",
            recommended_action="Configurar GEMINI_API_KEY en variables de entorno",
            confidence=0.0
        )
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read image
        image_bytes = await file.read()
        image_b64 = base64.b64encode(image_bytes).decode()
        
        # Expert prompt
        prompt = """Actúa como un experto en Facility Management con 8 años de experiencia. 
Analiza esta foto técnica de un local comercial e identifica:

1. Tipo de avería o problema detectado
2. Nivel de riesgo (Crítico/Medio/Bajo)
3. Acción inmediata sugerida

Responde en formato JSON con estas claves exactas:
{
  "diagnosis": "descripción técnica del problema",
  "severity": "Alta/Media/Baja",
  "recommended_action": "acción específica a tomar",
  "confidence": 0.95
}"""
        
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_b64}])
        
        # Parse JSON response
        import json
        result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        
        return TriageResult(**result)
        
    except Exception as e:
        # Fallback on error
        return TriageResult(
            diagnosis=f"Error en análisis IA: {str(e)}",
            severity="Media",
            recommended_action="Revisar manualmente la imagen",
            confidence=0.0
        )


@app.get("/alerts/legal", response_model=List[LegalAlert])
def get_legal_alerts():
    """
    Checks for expiring certifications (SEC, Gas, Extinguishers).
    """
    alerts = []
    # Mock some certifications linked to assets or store
    certs = [
        {"title": "SEC Electrical Certification", "expires": datetime.now() + timedelta(days=45)},
        {"title": "Gas Seal (Sello Verde)", "expires": datetime.now() - timedelta(days=5)}, # Expired!
        {"title": "Fire Extinguisher Check", "expires": datetime.now() + timedelta(days=5)} # Urgent
    ]
    
    for c in certs:
        days = (c["expires"] - datetime.now()).days
        severity = "low"
        if days < 0:
            severity = "high" # Expired
        elif days < 7:
            severity = "high" # Urgent
        elif days < 30:
            severity = "medium"
            
        alerts.append(LegalAlert(
            id=str(random.randint(1000, 9999)),
            title=c["title"],
            due_date=c["expires"],
            days_remaining=days,
            severity=severity
        ))
    return alerts

@app.post("/payments/initiate")
def initiate_payment(amount: int, provider: str = "webpay"):
    """
    Placeholder for Payment Gateway Integration (Flow/Webpay).
    """
    return {
        "status": "pending",
        "provider": provider,
        "amount_clp": amount,
        "redirect_url": f"https://mock-payment-gateway.cl/pay?amt={amount}&ref=KER-{random.randint(10000,99999)}"
    }
