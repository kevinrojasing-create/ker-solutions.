from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class AssetDB(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    install_date = Column(DateTime)
    last_maintenance = Column(DateTime)
    usage_hours_per_day = Column(Float)
    maintenance_interval_days = Column(Integer, default=180)
    image_url = Column(String, nullable=True)

class TicketDB(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    severity = Column(String)
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.now)
    # Could link to AssetDB.id via ForeignKey in a full app
