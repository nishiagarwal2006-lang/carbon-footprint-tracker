"""
Insights Engine

Generates personalized recommendations and insights based on:
- User's carbon footprint data
- Trends and patterns
- Available actions and their impact
- Behavioral patterns
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Insight as InsightModel, CarbonFootprint, Action, User
from carbon_calculator import CarbonCalculator, GLOBAL_AVERAGES, CARBON_BENCHMARKS


class InsightsEngine:
    """Generate personalized carbon reduction insights"""

    def __init__(self, db: Session):
        self.db = db
        self.calculator = CarbonCalculator()

    def generate_all_insights(self, user_id: int) -> List[InsightModel]:
        """
        Generate all insights for a user
        
        Returns:
            List of Insight objects
        """
        insights = []
        
        # Get user data
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return insights
        
        # Generate different types of insights
        insights.extend(self._generate_trend_insights(user_id))
        insights.extend(self._generate_opportunity_insights(user_id))
        insights.extend(self._generate_milestone_insights(user_id))
        insights.extend(self._generate_behavior_insights(user_id))
        
        return insights

    def _generate_trend_insights(self, user_id: int) -> List[InsightModel]:
        """
        Generate insights based on carbon trends
        
        Returns:
            List of trend-based insights
        """
        insights = []
        
        # Get last 30 days of data
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        footprints = self.db.query(CarbonFootprint).filter(
            CarbonFootprint.user_id == user_id,
            CarbonFootprint.date >= thirty_days_ago
        ).all()
        
        if len(footprints) < 5:
            return insights
        
        # Calculate trend
        first_week_avg = sum([f.total_co2 for f in footprints[:7]]) / 7
        last_week_avg = sum([f.total_co2 for f in footprints[-7:]]) / 7
        trend_change = ((last_week_avg - first_week_avg) / first_week_avg) * 100
        
        if trend_change < -10:
            insight = InsightModel(
                user_id=user_id,
                title="Great Progress! 🎉",
                description=f"Your carbon footprint decreased by {abs(trend_change):.1f}% in the last month. Keep up the good work!",
                category="milestone",
                co2_impact=abs(last_week_avg - first_week_avg),
                priority="high",
                is_read=False
            )
            insights.append(insight)
        elif trend_change > 10:
            insight = InsightModel(
                user_id=user_id,
                title="Footprint Increasing ⚠️",
                description=f"Your carbon footprint increased by {trend_change:.1f}% recently. Review your activities to find areas to reduce.",
                category="warning",
                co2_impact=0,
                priority="high",
                is_read=False
            )
            insights.append(insight)
        
        return insights

    def _generate_opportunity_insights(self, user_id: int) -> List[InsightModel]:
        """
        Generate insights about reduction opportunities
        
        Returns:
            List of opportunity-based insights
        """
        insights = []
        
        # Get latest footprint
        latest = self.db.query(CarbonFootprint).filter(
            CarbonFootprint.user_id == user_id
        ).order_by(CarbonFootprint.date.desc()).first()
        
        if not latest:
            return insights
        
        # Analyze biggest emitters
        categories = [
            ("energy", latest.energy_co2, "Energy Use"),
            ("transport", latest.transport_co2, "Transportation"),
            ("diet", latest.diet_co2, "Diet"),
            ("lifestyle", latest.lifestyle_co2, "Lifestyle"),
        ]
        
        categories.sort(key=lambda x: x[1], reverse=True)
        
        # Top emitter insight
        if categories[0][1] > 0:
            top_category = categories[0]
            
            if top_category[0] == "transport" and latest.transport_co2 > 2:
                insight = InsightModel(
                    user_id=user_id,
                    title="🚗 Transportation Opportunity",
                    description=f"Transportation is your largest emitter ({top_category[1]:.1f} kg CO2 daily). Switching to public transport 2x/week could save ~{0.121 * 20:.1f} kg/week.",
                    category="opportunity",
                    co2_impact=0.121 * 20,
                    priority="high",
                    is_read=False
                )
                insights.append(insight)
            
            elif top_category[0] == "energy" and latest.energy_co2 > 3:
                insight = InsightModel(
                    user_id=user_id,
                    title="⚡ Energy Efficiency Tip",
                    description=f"Your daily energy use is {latest.energy_co2:.1f} kg CO2. Consider LED bulbs, better insulation, or renewable energy. Could save ~{0.4 * 5:.1f} kg/day.",
                    category="opportunity",
                    co2_impact=0.4 * 5,
                    priority="medium",
                    is_read=False
                )
                insights.append(insight)
            
            elif top_category[0] == "diet" and latest.diet_co2 > 3:
                insight = InsightModel(
                    user_id=user_id,
                    title="🥗 Diet Opportunity",
                    description=f"Switching to a vegetarian diet could save ~{latest.diet_co2 - 2.5:.1f} kg CO2/day. Start with Meatless Mondays!",
                    category="opportunity",
                    co2_impact=latest.diet_co2 - 2.5,
                    priority="medium",
                    is_read=False
                )
                insights.append(insight)
        
        return insights

    def _generate_milestone_insights(self, user_id: int) -> List[InsightModel]:
        """
        Generate milestone insights when user reaches targets
        
        Returns:
            List of milestone insights
        """
        insights = []
        
        # Calculate monthly footprint
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_co2 = self.db.query(CarbonFootprint).filter(
            CarbonFootprint.user_id == user_id,
            CarbonFootprint.date >= thirty_days_ago
        ).all()
        
        if not monthly_co2:
            return insights
        
        total_monthly = sum([f.total_co2 for f in monthly_co2])
        days = len(monthly_co2)
        daily_avg = total_monthly / days if days > 0 else 0
        monthly_total = daily_avg * 30
        
        # Compare to benchmarks
        if monthly_total < CARBON_BENCHMARKS["low_footprint"]:
            insight = InsightModel(
                user_id=user_id,
                title="🌱 Low Carbon Champion",
                description=f"Excellent! Your projected annual footprint ({monthly_total * 12:.0f} kg) is well below the global average. You're making a real difference!",
                category="milestone",
                co2_impact=CARBON_BENCHMARKS["low_footprint"] - monthly_total,
                priority="high",
                is_read=False
            )
            insights.append(insight)
        
        # Check for 5-action completion
        active_actions = self.db.query(Action).filter(
            Action.user_id == user_id,
            Action.is_active == True
        ).count()
        
        if active_actions >= 5:
            insight = InsightModel(
                user_id=user_id,
                title="🎯 Action Master",
                description=f"You're tracking {active_actions} carbon reduction actions! This consistency is key to creating lasting change.",
                category="milestone",
                co2_impact=0,
                priority="low",
                is_read=False
            )
            insights.append(insight)
        
        return insights

    def _generate_behavior_insights(self, user_id: int) -> List[InsightModel]:
        """
        Generate insights based on user behavior patterns
        
        Returns:
            List of behavior-based insights
        """
        insights = []
        
        # Check if user has logged actions
        actions = self.db.query(Action).filter(
            Action.user_id == user_id,
            Action.is_active == True
        ).all()
        
        if not actions:
            insight = InsightModel(
                user_id=user_id,
                title="📋 Start Tracking Actions",
                description="You haven't logged any carbon reduction actions yet. Start with one simple action like using public transport once a week!",
                category="recommendation",
                co2_impact=0,
                priority="medium",
                is_read=False
            )
            insights.append(insight)
        
        # Check consistency
        if len(actions) > 0:
            total_completions = sum([a.total_occurrences for a in actions])
            if total_completions == 0:
                insight = InsightModel(
                    user_id=user_id,
                    title="💪 Start Small",
                    description="You've added actions but haven't logged completions yet. Start tracking today - even small actions add up!",
                    category="recommendation",
                    co2_impact=0,
                    priority="medium",
                    is_read=False
                )
                insights.append(insight)
        
        return insights

    def get_personalized_recommendations(self, user_id: int, count: int = 5) -> List[Dict]:
        """
        Get top N personalized recommendations
        
        Returns:
            List of recommendation dictionaries
        """
        latest = self.db.query(CarbonFootprint).filter(
            CarbonFootprint.user_id == user_id
        ).order_by(CarbonFootprint.date.desc()).first()
        
        if not latest:
            return []
        
        recommendations = []
        
        # Transport recommendations
        if latest.transport_type == "car" and latest.transport_km > 10:
            recommendations.append({
                "id": "transport_1",
                "title": "Switch to public transport",
                "description": "Reduces CO2 by 60% compared to driving",
                "co2_saved": 0.121 * latest.transport_km,
                "difficulty": "medium",
                "category": "transport"
            })
        
        if latest.transport_km > 50:
            recommendations.append({
                "id": "transport_2",
                "title": "Work from home once a week",
                "description": "Saves commute emissions",
                "co2_saved": 0.21 * 50,  # Assume 50km round trip
                "difficulty": "easy",
                "category": "transport"
            })
        
        # Energy recommendations
        if latest.energy_kwh > 10:
            recommendations.append({
                "id": "energy_1",
                "title": "Switch to renewable energy",
                "description": "Eliminates fossil fuel emissions",
                "co2_saved": latest.energy_co2,
                "difficulty": "hard",
                "category": "energy"
            })
        
        # Diet recommendations
        if latest.diet_type in ["meat_heavy", "mixed"]:
            recommendations.append({
                "id": "diet_1",
                "title": "Try Meatless Mondays",
                "description": "Reduce meat consumption one day a week",
                "co2_saved": 2.0,  # Approximate reduction
                "difficulty": "easy",
                "category": "diet"
            })
        
        # Lifestyle recommendations
        recommendations.append({
            "id": "lifestyle_1",
            "title": "Reduce shopping frequency",
            "description": "Buy only what you need",
            "co2_saved": 2.0,
            "difficulty": "easy",
            "category": "lifestyle"
        })
        
        return recommendations[:count]