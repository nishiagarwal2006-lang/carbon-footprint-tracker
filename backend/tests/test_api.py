"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from database import SessionLocal, Base, engine

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_health_check():
    """Test API health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_user():
    """Test user creation"""
    response = client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "language": "en"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_add_carbon_footprint():
    """Test adding carbon footprint"""
    # Create user first
    user_response = client.post("/api/users", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "language": "en"
    })
    user_id = user_response.json()["id"]
    
    # Add footprint
    response = client.post(f"/api/carbon-footprint/{user_id}", json={
        "energy_kwh": 10,
        "transport_km": 20,
        "transport_type": "car",
        "diet_type": "mixed"
    })
    assert response.status_code == 200
    assert response.json()["total_co2"] > 0


def test_get_dashboard():
    """Test dashboard endpoint"""
    # Create user
    user_response = client.post("/api/users", json={
        "username": "testuser3",
        "email": "test3@example.com",
        "language": "en"
    })
    user_id = user_response.json()["id"]
    
    # Get dashboard
    response = client.get(f"/api/dashboard/{user_id}")
    assert response.status_code == 200
    assert "current_stats" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])