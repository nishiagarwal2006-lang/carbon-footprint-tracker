"""
Unit tests for carbon calculator module
"""

import pytest
from carbon_calculator import CarbonCalculator


class TestCarbonCalculator:
    """Test cases for CarbonCalculator"""
    
    def test_calculate_energy_co2_electricity(self):
        """Test electricity CO2 calculation"""
        co2 = CarbonCalculator.calculate_energy_co2(10)  # 10 kWh
        assert co2 == 4.0  # 10 * 0.4
        assert isinstance(co2, float)
    
    def test_calculate_energy_co2_with_gas(self):
        """Test gas heating CO2 calculation"""
        co2 = CarbonCalculator.calculate_energy_co2(10, 5)  # 10 kWh, 5 m³ gas
        assert co2 == 4.0 + (5 * 2.04)  # 14.2
        assert abs(co2 - 14.2) < 0.01
    
    def test_calculate_transport_car(self):
        """Test car transport CO2 calculation"""
        co2 = CarbonCalculator.calculate_transport_co2(100, "car")
        assert co2 == 21.0  # 100 * 0.21
    
    def test_calculate_transport_public(self):
        """Test public transport CO2 calculation"""
        co2 = CarbonCalculator.calculate_transport_co2(100, "public_transport")
        assert co2 == 8.9  # 100 * 0.089
        assert co2 < CarbonCalculator.calculate_transport_co2(100, "car")
    
    def test_calculate_transport_bike(self):
        """Test bike transport CO2 calculation"""
        co2 = CarbonCalculator.calculate_transport_co2(100, "bike")
        assert co2 == 0  # Zero emissions
    
    def test_calculate_transport_flight(self):
        """Test flight CO2 calculation"""
        co2 = CarbonCalculator.calculate_transport_co2(1000, "flight")
        assert co2 == 255.0  # 1000 * 0.255
    
    def test_calculate_diet_vegan(self):
        """Test vegan diet CO2 calculation"""
        co2 = CarbonCalculator.calculate_diet_co2("vegan", 1)
        assert co2 == 1.5
    
    def test_calculate_diet_vegetarian(self):
        """Test vegetarian diet CO2 calculation"""
        co2 = CarbonCalculator.calculate_diet_co2("vegetarian", 1)
        assert co2 == 2.5
    
    def test_calculate_diet_mixed(self):
        """Test mixed diet CO2 calculation"""
        co2 = CarbonCalculator.calculate_diet_co2("mixed", 1)
        assert co2 == 4.5
    
    def test_calculate_diet_meat_heavy(self):
        """Test meat-heavy diet CO2 calculation"""
        co2 = CarbonCalculator.calculate_diet_co2("meat_heavy", 1)
        assert co2 == 7.0
    
    def test_calculate_diet_multiple_days(self):
        """Test diet calculation for multiple days"""
        co2_1_day = CarbonCalculator.calculate_diet_co2("mixed", 1)
        co2_7_days = CarbonCalculator.calculate_diet_co2("mixed", 7)
        assert co2_7_days == co2_1_day * 7
    
    def test_calculate_lifestyle_co2(self):
        """Test lifestyle activities CO2 calculation"""
        activities = {
            "shopping": 1,
            "waste_disposed": 2,
            "streaming": 5,
        }
        co2 = CarbonCalculator.calculate_lifestyle_co2(activities)
        expected = 1 * 2.0 + 2 * 0.5 + 5 * 0.04  # 3.2
        assert co2 == expected
    
    def test_calculate_lifestyle_empty(self):
        """Test lifestyle calculation with no activities"""
        co2 = CarbonCalculator.calculate_lifestyle_co2({})
        assert co2 == 0
    
    def test_calculate_daily_footprint_complete(self):
        """Test complete daily footprint calculation"""
        result = CarbonCalculator.calculate_daily_footprint(
            energy_kwh=10,
            transport_km=20,
            transport_type="car",
            diet_type="mixed",
            lifestyle_activities={"shopping": 1},
            gas_m3=0
        )
        
        assert "energy_co2" in result
        assert "transport_co2" in result
        assert "diet_co2" in result
        assert "lifestyle_co2" in result
        assert "total_co2" in result
        assert "breakdown" in result
        
        # Verify calculation
        expected_total = (
            10 * 0.4 +  # energy
            20 * 0.21 +  # transport
            4.5 +  # diet
            2.0  # lifestyle
        )
        assert result["total_co2"] == round(expected_total, 2)
    
    def test_calculate_daily_footprint_breakdown(self):
        """Test that breakdown matches individual calculations"""
        result = CarbonCalculator.calculate_daily_footprint(
            energy_kwh=15,
            transport_km=30,
            transport_type="public_transport",
            diet_type="vegetarian",
        )
        
        assert result["breakdown"]["energy"] == result["energy_co2"]
        assert result["breakdown"]["transport"] == result["transport_co2"]
        assert result["breakdown"]["diet"] == result["diet_co2"]
        assert result["breakdown"]["lifestyle"] == result["lifestyle_co2"]
    
    def test_get_co2_equivalents(self):
        """Test CO2 equivalents data"""
        equivalents = CarbonCalculator.get_co2_equivalents()
        
        assert "car_mile" in equivalents
        assert "flight_hour" in equivalents
        assert "tree_absorbs_annual" in equivalents
        assert all(isinstance(v, (int, float)) for v in equivalents.values())
    
    def test_calculate_reduction_potential(self):
        """Test reduction potential calculation"""
        potential = CarbonCalculator.calculate_reduction_potential(10)
        
        assert "public_transport_vs_car" in potential
        assert "vegetarian_diet" in potential
        assert "renewable_energy" in potential
        assert all(isinstance(v, (int, float)) for v in potential.values())
    
    def test_invalid_transport_type_defaults(self):
        """Test that invalid transport type defaults gracefully"""
        co2 = CarbonCalculator.calculate_transport_co2(100, "invalid_type")
        # Should default to car emissions
        assert co2 == CarbonCalculator.calculate_transport_co2(100, "car")
    
    def test_invalid_diet_type_defaults(self):
        """Test that invalid diet type defaults gracefully"""
        co2 = CarbonCalculator.calculate_diet_co2("invalid_diet", 1)
        # Should default to mixed diet
        assert co2 == 4.5


class TestCarbonCalculatorEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_values(self):
        """Test calculation with zero values"""
        result = CarbonCalculator.calculate_daily_footprint(
            energy_kwh=0,
            transport_km=0,
            diet_type="vegan"
        )
        
        assert result["energy_co2"] == 0
        assert result["transport_co2"] == 0
        assert result["total_co2"] == result["diet_co2"]
    
    def test_large_values(self):
        """Test calculation with large values"""
        result = CarbonCalculator.calculate_daily_footprint(
            energy_kwh=1000,
            transport_km=5000,
            diet_type="meat_heavy"
        )
        
        assert result["total_co2"] > 0
        assert all(isinstance(v, float) for k, v in result.items() if k != "breakdown")
    
    def test_float_precision(self):
        """Test that results are rounded correctly"""
        result = CarbonCalculator.calculate_daily_footprint(
            energy_kwh=3.33333,
            transport_km=7.77777,
        )
        
        # All values should be rounded to 2 decimal places
        assert result["energy_co2"] == round(3.33333 * 0.4, 2)
        assert isinstance(result["total_co2"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])