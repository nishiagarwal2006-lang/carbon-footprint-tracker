from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./carbon_tracker.db")

# Create engine and tables
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============== Models ==============

class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    language = Column(String, default="en")
    dark_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CarbonFootprint(Base):
    """Carbon footprint entry model"""
    __tablename__ = "carbon_footprints"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Carbon sources (in kg CO2e)
    energy_kwh = Column(Float, default=0)
    energy_co2 = Column(Float, default=0)
    
    transport_km = Column(Float, default=0)
    transport_type = Column(String, default="car")
    transport_co2 = Column(Float, default=0)
    
    diet_type = Column(String, default="mixed")
    diet_co2 = Column(Float, default=0)
    
    lifestyle_co2 = Column(Float, default=0)
    lifestyle_activities = Column(JSON, default={})
    
    total_co2 = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Action(Base):
    """User actions to reduce carbon footprint"""
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action_name = Column(String)
    category = Column(String)  # transport, energy, diet, lifestyle
    co2_saved = Column(Float)  # kg CO2 per occurrence
    frequency = Column(String, default="weekly")  # daily, weekly, monthly
    start_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    total_occurrences = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Insight(Base):
    """Personalized insights for users"""
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)  # recommendation, milestone, warning, opportunity
    co2_impact = Column(Float)  # Potential CO2 reduction
    priority = Column(String, default="medium")  # low, medium, high
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyLog(Base):
    """Daily carbon activity log"""
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    activity_type = Column(String)  # action_completed, measurement_taken
    activity_data = Column(JSON)
    co2_change = Column(Float)  # Positive (reduction) or negative (increase)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()