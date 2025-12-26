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
    db.add_all(assets)
    db.commit()

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
    Mock AI Vision Triage.
    In real production, this would send the image to a TensorFlow/PyTorch model
    or an API like GPT-4 Vision / Google Vertex AI Vision.
    """
    # Simulate processing delay
    # analyze(file.file)
    
    # Deterministic mock based on filename length or random
    outcomes = [
        {"d": "Cortocircuito Eléctrico Detectado", "s": "Alta", "r": "Cortar energía inmediatamente. Llamar a Electricista."},
        {"d": "Filtro HVAC Obstruido", "s": "Baja", "r": "Limpiar o reemplazar filtro de aire."},
        {"d": "Fuga de Agua", "s": "Media", "r": "Verificar apriete de válvula. Llamar a Gasfiter si persiste."},
    ]
    outcome = random.choice(outcomes)
    
    return TriageResult(
        diagnosis=outcome["d"],
        severity=outcome["s"],
        recommended_action=outcome["r"],
        confidence=round(random.uniform(0.85, 0.99), 2)
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
