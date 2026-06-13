"""
Utility functions for carbon footprint tracker backend
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from database import CarbonFootprint, Action, DailyLog, User
from carbon_calculator import CarbonCalculator, GLOBAL_AVERAGES


def calculate_monthly_stats(user_id: int, db: Session) -> Dict:
    """
    Calculate monthly carbon statistics for a user
    
    Returns:
        Dictionary with monthly stats
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.date >= thirty_days_ago
    ).all()
    
    if not footprints:
        return {
            "total_co2": 0,
            "daily_average": 0,
            "monthly_projected": 0,
            "trend": "stable",
            "breakdown": {}
        }
    
    total_co2 = sum([f.total_co2 for f in footprints])
    days = len(footprints)
    daily_avg = total_co2 / days if days > 0 else 0
    monthly_projected = daily_avg * 30
    
    # Calculate breakdown by category
    breakdown = {
        "energy": round(sum([f.energy_co2 for f in footprints]), 2),
        "transport": round(sum([f.transport_co2 for f in footprints]), 2),
        "diet": round(sum([f.diet_co2 for f in footprints]), 2),
        "lifestyle": round(sum([f.lifestyle_co2 for f in footprints]), 2),
    }
    
    # Determine trend
    if days >= 14:
        first_half = sum([f.total_co2 for f in footprints[:days//2]]) / (days//2)
        second_half = sum([f.total_co2 for f in footprints[days//2:]]) / (days - days//2)
        change = ((second_half - first_half) / first_half) * 100
        
        if change < -5:
            trend = "improving"
        elif change > 5:
            trend = "worsening"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return {
        "total_co2": round(total_co2, 2),
        "daily_average": round(daily_avg, 2),
        "monthly_projected": round(monthly_projected, 2),
        "trend": trend,
        "breakdown": breakdown,
        "days_tracked": days,
        "comparison_to_global": round((monthly_projected / GLOBAL_AVERAGES["global_annual"] * 12 - 1) * 100, 1)
    }


def calculate_action_impact(user_id: int, db: Session) -> Dict:
    """
    Calculate total CO2 saved from user actions
    
    Returns:
        Dictionary with action impact stats
    """
    actions = db.query(Action).filter(
        Action.user_id == user_id,
        Action.is_active == True
    ).all()
    
    total_co2_saved = 0
    category_breakdown = {}
    
    for action in actions:
        if action.frequency == "daily":
            frequency_multiplier = 365
        elif action.frequency == "weekly":
            frequency_multiplier = 52
        elif action.frequency == "monthly":
            frequency_multiplier = 12
        else:
            frequency_multiplier = 1
        
        annual_savings = action.co2_saved * action.total_occurrences * frequency_multiplier
        total_co2_saved += annual_savings
        
        if action.category not in category_breakdown:
            category_breakdown[action.category] = 0
        category_breakdown[action.category] += annual_savings
    
    return {
        "total_co2_saved_annually": round(total_co2_saved, 2),
        "total_co2_saved_monthly": round(total_co2_saved / 12, 2),
        "by_category": {k: round(v, 2) for k, v in category_breakdown.items()},
        "actions_count": len(actions),
        "total_completions": sum([a.total_occurrences for a in actions])
    }


def get_daily_trend(user_id: int, days: int, db: Session) -> Dict:
    """
    Get carbon footprint trend over N days
    
    Returns:
        Dictionary with dates and CO2 values
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.date >= start_date
    ).order_by(CarbonFootprint.date).all()
    
    trend_data = []
    for footprint in footprints:
        trend_data.append({
            "date": footprint.date.isoformat(),
            "co2": footprint.total_co2,
            "energy": footprint.energy_co2,
            "transport": footprint.transport_co2,
            "diet": footprint.diet_co2,
            "lifestyle": footprint.lifestyle_co2,
        })
    
    return {"trend": trend_data, "period_days": days}


def export_to_pdf(user_id: int, start_date: datetime, end_date: datetime, db: Session) -> str:
    """
    Generate PDF report of user's carbon footprint
    
    Returns:
        Path to generated PDF
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    # Query data
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.date >= start_date,
        CarbonFootprint.date <= end_date
    ).all()
    
    actions = db.query(Action).filter(
        Action.user_id == user_id,
        Action.is_active == True
    ).all()
    
    # Create PDF
    filename = f"carbon_report_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=30,
    )
    story.append(Paragraph("Carbon Footprint Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # User info
    story.append(Paragraph(f"<b>User:</b> {user.username}", styles['Normal']))
    story.append(Paragraph(f"<b>Period:</b> {start_date.date()} to {end_date.date()}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary stats
    if footprints:
        total_co2 = sum([f.total_co2 for f in footprints])
        daily_avg = total_co2 / len(footprints)
        
        story.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
        summary_data = [
            ["Metric", "Value"],
            ["Total CO2 Emissions", f"{total_co2:.2f} kg"],
            ["Daily Average", f"{daily_avg:.2f} kg"],
            ["Days Tracked", str(len(footprints))],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Actions taken
    if actions:
        story.append(Paragraph("<b>Active Reduction Actions</b>", styles['Heading2']))
        action_data = [["Action", "Category", "CO2 Saved (kg)", "Completions"]]
        
        for action in actions:
            action_data.append([
                action.action_name,
                action.category,
                f"{action.co2_saved:.2f}",
                str(action.total_occurrences)
            ])
        
        action_table = Table(action_data)
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(action_table)
    
    doc.build(story)
    return filename


def export_to_csv(user_id: int, start_date: datetime, end_date: datetime, db: Session) -> str:
    """
    Export carbon footprint data to CSV
    
    Returns:
        Path to generated CSV
    """
    import csv
    
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.date >= start_date,
        CarbonFootprint.date <= end_date
    ).all()
    
    filename = f"carbon_data_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Energy (kg CO2)', 'Transport (kg CO2)', 'Diet (kg CO2)', 
                      'Lifestyle (kg CO2)', 'Total (kg CO2)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for fp in footprints:
            writer.writerow({
                'Date': fp.date.isoformat(),
                'Energy (kg CO2)': f"{fp.energy_co2:.2f}",
                'Transport (kg CO2)': f"{fp.transport_co2:.2f}",
                'Diet (kg CO2)': f"{fp.diet_co2:.2f}",
                'Lifestyle (kg CO2)': f"{fp.lifestyle_co2:.2f}",
                'Total (kg CO2)': f"{fp.total_co2:.2f}",
            })
    
    return filename


def get_comparison_data(user_id: int, db: Session) -> Dict:
    """
    Get user's footprint comparison to averages
    
    Returns:
        Dictionary with comparison metrics
    """
    stats = calculate_monthly_stats(user_id, db)
    monthly_projected = stats["monthly_projected"]
    annual_projected = monthly_projected * 12
    
    return {
        "user_annual": round(annual_projected, 2),
        "global_average": GLOBAL_AVERAGES["global_annual"],
        "us_average": GLOBAL_AVERAGES["us_annual"],
        "uk_average": GLOBAL_AVERAGES["uk_annual"],
        "comparison_to_global": round((annual_projected - GLOBAL_AVERAGES["global_annual"]) / GLOBAL_AVERAGES["global_annual"] * 100, 1),
        "status": "below_average" if annual_projected < GLOBAL_AVERAGES["global_annual"] else "above_average"
    }