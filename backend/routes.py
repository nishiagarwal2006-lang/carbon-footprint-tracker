"""
API Routes for Carbon Footprint Tracker
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from database import (
    User, CarbonFootprint, Action, Insight, DailyLog, get_db
)
from models import (
    UserCreate, UserResponse, UserUpdate,
    CarbonFootprintCreate, CarbonFootprintResponse,
    ActionCreate, ActionResponse, ActionUpdate,
    InsightResponse, DailyLogCreate, DailyLogResponse,
    CarbonStats, DashboardResponse
)
from carbon_calculator import CarbonCalculator
from insights_engine import InsightsEngine
from utils import (
    calculate_monthly_stats, calculate_action_impact, get_daily_trend,
    export_to_pdf, export_to_csv, get_comparison_data
)

router = APIRouter()

# ============== User Endpoints ==============

@router.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        username=user.username,
        email=user.email,
        language=user.language
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user preferences"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.language:
        user.language = user_update.language
    if user_update.dark_mode is not None:
        user.dark_mode = user_update.dark_mode
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


# ============== Carbon Footprint Endpoints ==============

@router.post("/api/carbon-footprint/{user_id}", response_model=CarbonFootprintResponse)
def create_carbon_footprint(
    user_id: int,
    footprint: CarbonFootprintCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new carbon footprint entry
    
    Calculates CO2 from energy, transport, diet, and lifestyle
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate CO2 for each category
    calculator = CarbonCalculator()
    
    energy_co2 = calculator.calculate_energy_co2(footprint.energy_kwh)
    transport_co2 = calculator.calculate_transport_co2(
        footprint.transport_km,
        footprint.transport_type
    )
    diet_co2 = calculator.calculate_diet_co2(footprint.diet_type, 1)
    lifestyle_co2 = calculator.calculate_lifestyle_co2(
        footprint.lifestyle_activities or {}
    )
    
    total_co2 = energy_co2 + transport_co2 + diet_co2 + lifestyle_co2
    
    # Create database entry
    db_footprint = CarbonFootprint(
        user_id=user_id,
        energy_kwh=footprint.energy_kwh,
        energy_co2=energy_co2,
        transport_km=footprint.transport_km,
        transport_type=footprint.transport_type,
        transport_co2=transport_co2,
        diet_type=footprint.diet_type,
        diet_co2=diet_co2,
        lifestyle_co2=lifestyle_co2,
        lifestyle_activities=footprint.lifestyle_activities or {},
        total_co2=total_co2,
    )
    
    db.add(db_footprint)
    db.commit()
    db.refresh(db_footprint)
    
    # Log the activity
    log = DailyLog(
        user_id=user_id,
        activity_type="measurement_taken",
        activity_data={"category": "carbon_footprint", "total_co2": total_co2},
        co2_change=0  # This is a measurement, not a change
    )
    db.add(log)
    db.commit()
    
    return db_footprint


@router.get("/api/carbon-footprint/{user_id}", response_model=List[CarbonFootprintResponse])
def get_carbon_footprints(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get carbon footprint entries for a user (last N days)"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.date >= start_date
    ).order_by(CarbonFootprint.date.desc()).all()
    
    return footprints


# ============== Action Endpoints ==============

@router.post("/api/actions/{user_id}", response_model=ActionResponse)
def create_action(
    user_id: int,
    action: ActionCreate,
    db: Session = Depends(get_db)
):
    """Create a new carbon reduction action"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_action = Action(
        user_id=user_id,
        action_name=action.action_name,
        category=action.category,
        co2_saved=action.co2_saved,
        frequency=action.frequency
    )
    
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    
    return db_action


@router.get("/api/actions/{user_id}", response_model=List[ActionResponse])
def get_actions(user_id: int, db: Session = Depends(get_db)):
    """Get all actions for a user"""
    actions = db.query(Action).filter(
        Action.user_id == user_id,
        Action.is_active == True
    ).all()
    
    return actions


@router.put("/api/actions/{action_id}", response_model=ActionResponse)
def update_action(
    action_id: int,
    action_update: ActionUpdate,
    db: Session = Depends(get_db)
):
    """Update an action"""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action_update.is_active is not None:
        action.is_active = action_update.is_active
    
    if action_update.total_occurrences is not None:
        action.total_occurrences = action_update.total_occurrences
    
    db.commit()
    db.refresh(action)
    
    # Log the action completion
    if action_update.total_occurrences is not None:
        log = DailyLog(
            user_id=action.user_id,
            activity_type="action_completed",
            activity_data={"action_id": action.id, "action_name": action.action_name},
            co2_change=action.co2_saved  # Positive = reduction
        )
        db.add(log)
        db.commit()
    
    return action


@router.delete("/api/actions/{action_id}")
def delete_action(action_id: int, db: Session = Depends(get_db)):
    """Deactivate an action"""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action.is_active = False
    db.commit()
    
    return {"message": "Action deactivated"}


# ============== Insights Endpoints ==============

@router.get("/api/insights/{user_id}", response_model=List[InsightResponse])
def get_insights(user_id: int, db: Session = Depends(get_db)):
    """Get insights for a user"""
    insights = db.query(Insight).filter(
        Insight.user_id == user_id
    ).order_by(Insight.created_at.desc()).all()
    
    return insights


@router.post("/api/insights/generate/{user_id}")
def generate_insights(user_id: int, db: Session = Depends(get_db)):
    """Generate personalized insights for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    engine = InsightsEngine(db)
    
    # Clear old insights (keep last 10)
    old_insights = db.query(Insight).filter(
        Insight.user_id == user_id
    ).order_by(Insight.created_at.desc()).offset(10).all()
    
    for insight in old_insights:
        db.delete(insight)
    
    # Generate new insights
    new_insights = engine.generate_all_insights(user_id)
    
    for insight in new_insights:
        db.add(insight)
    
    db.commit()
    
    return {
        "message": f"Generated {len(new_insights)} insights",
        "count": len(new_insights)
    }


@router.put("/api/insights/{insight_id}/read")
def mark_insight_read(insight_id: int, db: Session = Depends(get_db)):
    """Mark an insight as read"""
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_read = True
    db.commit()
    
    return {"message": "Insight marked as read"}


# ============== Dashboard Endpoints ==============

@router.get("/api/dashboard/{user_id}", response_model=DashboardResponse)
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Get complete dashboard data for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get stats
    stats = calculate_monthly_stats(user_id, db)
    action_impact = calculate_action_impact(user_id, db)
    
    carbon_stats = CarbonStats(
        total_co2_month=stats["total_co2"],
        total_co2_saved=action_impact["total_co2_saved_monthly"],
        footprint_trend=list(range(10)),  # Placeholder
        daily_average=stats["daily_average"],
        top_emitter_category=max(
            stats["breakdown"].items(), key=lambda x: x[1]
        )[0] if stats["breakdown"] else "unknown",
        comparison_to_avg=0.0
    )
    
    # Get actions and insights
    actions = db.query(Action).filter(
        Action.user_id == user_id,
        Action.is_active == True
    ).all()
    
    insights = db.query(Insight).filter(
        Insight.user_id == user_id
    ).order_by(Insight.created_at.desc()).limit(5).all()
    
    # Get recent logs
    logs = db.query(DailyLog).filter(
        DailyLog.user_id == user_id
    ).order_by(DailyLog.created_at.desc()).limit(10).all()
    
    return DashboardResponse(
        user=user,
        current_stats=carbon_stats,
        actions=actions,
        insights=insights,
        recent_logs=logs
    )


# ============== Statistics Endpoints ==============

@router.get("/api/stats/{user_id}")
def get_statistics(user_id: int, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get detailed statistics for a user"""
    monthly_stats = calculate_monthly_stats(user_id, db)
    action_impact = calculate_action_impact(user_id, db)
    trend = get_daily_trend(user_id, days, db)
    comparison = get_comparison_data(user_id, db)
    
    return {
        "monthly_stats": monthly_stats,
        "action_impact": action_impact,
        "trend": trend,
        "comparison": comparison,
    }


@router.get("/api/recommendations/{user_id}")
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Get personalized recommendations for a user"""
    engine = InsightsEngine(db)
    recommendations = engine.get_personalized_recommendations(user_id, count=5)
    
    return {"recommendations": recommendations}


# ============== Export Endpoints ==============

@router.post("/api/export/pdf/{user_id}")
def export_pdf(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Export carbon data to PDF"""
    filename = export_to_pdf(user_id, start_date, end_date, db)
    
    return {
        "filename": filename,
        "format": "pdf",
        "message": "PDF generated successfully"
    }


@router.post("/api/export/csv/{user_id}")
def export_csv(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Export carbon data to CSV"""
    filename = export_to_csv(user_id, start_date, end_date, db)
    
    return {
        "filename": filename,
        "format": "csv",
        "message": "CSV generated successfully"
    }


# ============== Health Check ==============
@router.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}