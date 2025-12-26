from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class AssetDB(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    install_date = Column(DateTime, nullable=False)
    last_maintenance = Column(DateTime, nullable=False)
    usage_hours_per_day = Column(Float, nullable=False)
    maintenance_interval_days = Column(Integer, default=180)
    image_url = Column(String, nullable=True)

class TicketDB(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(String, nullable=True)  # Optional: link to asset
    description = Column(String, nullable=False)
    priority = Column(String, nullable=False)  # "Alta", "Media", "Baja"
    status = Column(String, default="Pendiente")  # "Pendiente", "En Proceso", "Resuelto"
    image_base64 = Column(String, nullable=True)  # Store image as base64
    created_at = Column(DateTime, nullable=False)
    ai_diagnosis = Column(String, nullable=True)  # AI analysis result
