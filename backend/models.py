from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# ============== User Models ==============

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    language: str = "en"


class UserUpdate(BaseModel):
    language: Optional[str] = None
    dark_mode: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    language: str
    dark_mode: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Carbon Footprint Models ==============

class CarbonFootprintCreate(BaseModel):
    energy_kwh: float
    transport_km: float
    transport_type: str  # car, public_transport, bike, walk
    diet_type: str  # vegan, vegetarian, mixed, meat_heavy
    lifestyle_co2: Optional[float] = 0
    lifestyle_activities: Optional[Dict] = None


class CarbonFootprintResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    energy_co2: float
    transport_co2: float
    diet_co2: float
    lifestyle_co2: float
    total_co2: float
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Action Models ==============

class ActionCreate(BaseModel):
    action_name: str
    category: str  # transport, energy, diet, lifestyle
    co2_saved: float
    frequency: str = "weekly"


class ActionUpdate(BaseModel):
    is_active: Optional[bool] = None
    total_occurrences: Optional[int] = None


class ActionResponse(BaseModel):
    id: int
    user_id: int
    action_name: str
    category: str
    co2_saved: float
    frequency: str
    start_date: datetime
    is_active: bool
    total_occurrences: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Insight Models ==============

class InsightResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category: str
    co2_impact: float
    priority: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Daily Log Models ==============

class DailyLogCreate(BaseModel):
    activity_type: str
    activity_data: Dict
    co2_change: float


class DailyLogResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    activity_type: str
    activity_data: Dict
    co2_change: float
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Statistics Models ==============

class CarbonStats(BaseModel):
    total_co2_month: float
    total_co2_saved: float
    footprint_trend: List[float]
    daily_average: float
    top_emitter_category: str
    comparison_to_avg: float  # percentage


class DashboardResponse(BaseModel):
    user: UserResponse
    current_stats: CarbonStats
    actions: List[ActionResponse]
    insights: List[InsightResponse]
    recent_logs: List[DailyLogResponse]


# ============== Export Models ==============

class ExportRequest(BaseModel):
    format: str  # "pdf" or "csv"
    start_date: datetime
    end_date: datetime


class ExportResponse(BaseModel):
    filename: str
    url: str
    created_at: datetime