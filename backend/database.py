import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get DB URL from Environment (Render) or fallback to Local SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ker.db")

# Fix Render's "postgres://" -> SQLAlchemy's "postgresql://"
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires specific args, PostgreSQL requires SSL on Render
connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "postgresql" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"connect_timeout": 10}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
