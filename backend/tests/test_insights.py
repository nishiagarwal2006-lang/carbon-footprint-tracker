"""
Unit tests for insights engine module
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, CarbonFootprint, Action, Insight
from insights_engine import InsightsEngine
from carbon_calculator import GLOBAL_AVERAGES


# Create in-memory SQLite database for testing
@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()


@pytest.fixture
def test_user(test_db):
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        language="en",
        dark_mode=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_footprints(test_db, test_user):
    """Create test carbon footprints"""
    footprints = []
    
    # Create 30 days of footprint data
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=29-i)
        
        # Decreasing trend over time
        energy_co2 = 3.0 - (i * 0.05)
        transport_co2 = 4.0 - (i * 0.03)
        diet_co2 = 4.5
        lifestyle_co2 = 0.5
        
        footprint = CarbonFootprint(
            user_id=test_user.id,
            date=date,
            energy_kwh=10,
            energy_co2=energy_co2,
            transport_km=20,
            transport_type="car",
            transport_co2=transport_co2,
            diet_type="mixed",
            diet_co2=diet_co2,
            lifestyle_co2=lifestyle_co2,
            total_co2=energy_co2 + transport_co2 + diet_co2 + lifestyle_co2
        )
        test_db.add(footprint)
        footprints.append(footprint)
    
    test_db.commit()
    return footprints


class TestInsightsEngine:
    """Test cases for InsightsEngine"""
    
    def test_engine_initialization(self, test_db):
        """Test insights engine initialization"""
        engine = InsightsEngine(test_db)
        assert engine.db is test_db
        assert engine.calculator is not None
    
    def test_generate_all_insights(self, test_db, test_user, test_footprints):
        """Test generating all insights for a user"""
        engine = InsightsEngine(test_db)
        insights = engine.generate_all_insights(test_user.id)
        
        assert isinstance(insights, list)
        # Should generate at least some insights
        assert len(insights) > 0
    
    def test_generate_trend_insights_improving(self, test_db, test_user, test_footprints):
        """Test trend insights for improving footprint"""
        engine = InsightsEngine(test_db)
        insights = engine._generate_trend_insights(test_user.id)
        
        # With decreasing trend, should have a positive insight
        assert len(insights) > 0
        assert any("Progress" in i.title or "Improving" in i.title.lower() for i in insights)
    
    def test_generate_opportunity_insights(self, test_db, test_user, test_footprints):
        """Test opportunity-based insights"""
        engine = InsightsEngine(test_db)
        insights = engine._generate_opportunity_insights(test_user.id)
        
        assert isinstance(insights, list)
        assert all(i.category == "opportunity" for i in insights)
    
    def test_generate_milestone_insights_low_footprint(self, test_db, test_user):
        """Test milestone insights for low carbon footprint"""
        # Create low footprint entries
        for i in range(10):
            footprint = CarbonFootprint(
                user_id=test_user.id,
                energy_co2=1.0,
                transport_co2=0.5,
                diet_co2=1.5,
                lifestyle_co2=0,
                total_co2=3.0
            )
            test_db.add(footprint)
        test_db.commit()
        
        engine = InsightsEngine(test_db)
        insights = engine._generate_milestone_insights(test_user.id)
        
        # Should have a low carbon champion milestone
        assert any("Champion" in i.title for i in insights)
    
    def test_generate_behavior_insights_no_actions(self, test_db, test_user, test_footprints):
        """Test behavior insights when no actions logged"""
        engine = InsightsEngine(test_db)
        insights = engine._generate_behavior_insights(test_user.id)
        
        # Should suggest starting to track actions
        assert len(insights) > 0
        assert any("action" in i.title.lower() for i in insights)
    
    def test_generate_behavior_insights_with_actions(self, test_db, test_user, test_footprints):
        """Test behavior insights with active actions"""
        action = Action(
            user_id=test_user.id,
            action_name="Use public transport",
            category="transport",
            co2_saved=2.0,
            frequency="weekly",
            is_active=True,
            total_occurrences=0
        )
        test_db.add(action)
        test_db.commit()
        
        engine = InsightsEngine(test_db)
        insights = engine._generate_behavior_insights(test_user.id)
        
        # Should suggest starting to log completions
        assert any("track" in i.title.lower() or "start" in i.title.lower() for i in insights)
    
    def test_get_personalized_recommendations(self, test_db, test_user, test_footprints):
        """Test getting personalized recommendations"""
        engine = InsightsEngine(test_db)
        recommendations = engine.get_personalized_recommendations(test_user.id, count=5)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        assert all("title" in r and "description" in r for r in recommendations)
    
    def test_recommendations_structure(self, test_db, test_user, test_footprints):
        """Test recommendation data structure"""
        engine = InsightsEngine(test_db)
        recommendations = engine.get_personalized_recommendations(test_user.id, count=3)
        
        if len(recommendations) > 0:
            rec = recommendations[0]
            assert "id" in rec
            assert "title" in rec
            assert "description" in rec
            assert "co2_saved" in rec
            assert "difficulty" in rec
            assert "category" in rec
    
    def test_no_recommendations_without_data(self, test_db, test_user):
        """Test that no recommendations are generated without footprint data"""
        engine = InsightsEngine(test_db)
        recommendations = engine.get_personalized_recommendations(test_user.id)
        
        assert recommendations == []
    
    def test_transport_recommendations(self, test_db, test_user):
        """Test transport-specific recommendations"""
        # Create high transport footprint
        footprint = CarbonFootprint(
            user_id=test_user.id,
            energy_co2=2.0,
            transport_km=100,
            transport_type="car",
            transport_co2=21.0,
            diet_co2=4.5,
            lifestyle_co2=0.5,
            total_co2=28.5
        )
        test_db.add(footprint)
        test_db.commit()
        
        engine = InsightsEngine(test_db)
        recommendations = engine.get_personalized_recommendations(test_user.id)
        
        # Should have transport recommendations
        assert any(r["category"] == "transport" for r in recommendations)
    
    def test_diet_recommendations(self, test_db, test_user):
        """Test diet-specific recommendations"""
        footprint = CarbonFootprint(
            user_id=test_user.id,
            energy_co2=2.0,
            transport_co2=4.0,
            diet_type="meat_heavy",
            diet_co2=7.0,
            lifestyle_co2=0.5,
            total_co2=13.5
        )
        test_db.add(footprint)
        test_db.commit()
        
        engine = InsightsEngine(test_db)
        recommendations = engine.get_personalized_recommendations(test_user.id)
        
        # Should have diet recommendations
        assert any(r["category"] == "diet" for r in recommendations)


class TestInsightsContent:
    """Test the quality and content of generated insights"""
    
    def test_insight_has_required_fields(self, test_db, test_user, test_footprints):
        """Test that insights have all required fields"""
        engine = InsightsEngine(test_db)
        insights = engine.generate_all_insights(test_user.id)
        
        for insight in insights:
            assert hasattr(insight, "title")
            assert hasattr(insight, "description")
            assert hasattr(insight, "category")
            assert hasattr(insight, "co2_impact")
            assert hasattr(insight, "priority")
            assert insight.user_id == test_user.id
    
    def test_insight_categories(self, test_db, test_user, test_footprints):
        """Test that insights have valid categories"""
        engine = InsightsEngine(test_db)
        insights = engine.generate_all_insights(test_user.id)
        
        valid_categories = {"recommendation", "milestone", "warning", "opportunity"}
        
        for insight in insights:
            assert insight.category in valid_categories
    
    def test_insight_priorities(self, test_db, test_user, test_footprints):
        """Test that insights have valid priorities"""
        engine = InsightsEngine(test_db)
        insights = engine.generate_all_insights(test_user.id)
        
        valid_priorities = {"low", "medium", "high"}
        
        for insight in insights:
            assert insight.priority in valid_priorities
    
    def test_insight_co2_impact(self, test_db, test_user, test_footprints):
        """Test that insights have valid CO2 impact values"""
        engine = InsightsEngine(test_db)
        insights = engine.generate_all_insights(test_user.id)
        
        for insight in insights:
            assert isinstance(insight.co2_impact, (int, float))
            assert insight.co2_impact >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])