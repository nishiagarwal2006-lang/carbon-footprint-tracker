"""
Carbon Footprint Calculator

Calculates CO2 emissions based on user activities:
- Energy consumption (electricity, gas, heating)
- Transport (car, public transport, flights, cycling)
- Diet (vegan, vegetarian, mixed, meat-heavy)
- Lifestyle (shopping, waste, water usage)

All calculations return CO2 equivalent (CO2e) in kilograms
Based on IPCC and EPA emission factors
"""

from typing import Dict


class CarbonCalculator:
    """
    Calculates carbon footprint from various sources
    
    Emission factors (kg CO2e per unit):
    - Electricity: varies by grid (using global average ~0.4 kg/kWh)
    - Gas heating: 2.04 kg CO2 per m³
    - Car: 0.21 kg CO2 per km (average car)
    - Public transport: 0.089 kg CO2 per km
    - Bike: 0 kg CO2
    - Flight: 0.255 kg CO2 per km
    - Diet varies by type
    """
    
    # Emission factors (kg CO2e per unit)
    ELECTRICITY_EMISSION = 0.4  # kg CO2 per kWh (global average)
    GAS_EMISSION = 2.04  # kg CO2 per m³
    
    # Transport emissions (kg CO2 per km)
    TRANSPORT_EMISSIONS = {
        "car": 0.21,
        "public_transport": 0.089,
        "bike": 0,
        "walk": 0,
        "flight": 0.255,
    }
    
    # Daily diet emissions (kg CO2 per day)
    DIET_EMISSIONS = {
        "vegan": 1.5,
        "vegetarian": 2.5,
        "mixed": 4.5,
        "meat_heavy": 7.0,
    }
    
    # Lifestyle activities (kg CO2 per activity)
    LIFESTYLE_ACTIVITIES = {
        "shopping": 2.0,  # Average shopping trip
        "waste_disposed": 0.5,  # Per kg of waste
        "water_usage": 0.3,  # Per 100L
        "streaming": 0.04,  # Per hour
        "gaming": 0.08,  # Per hour
        "laundry": 0.7,  # Per wash cycle
        "heating_per_degree": 10.0,  # Per degree above comfortable temp
    }
    
    # Annual lifestyle baseline (things we do regularly)
    ANNUAL_BASELINE = {
        "personal_care": 45,  # kg CO2/year
        "home_maintenance": 50,  # kg CO2/year
        "furniture_replacement": 100,  # kg CO2/year
    }

    @staticmethod
    def calculate_energy_co2(kwh: float, gas_m3: float = 0) -> float:
        """
        Calculate CO2 from electricity and gas usage
        
        Args:
            kwh: Daily electricity consumption in kWh
            gas_m3: Daily gas consumption in cubic meters
        
        Returns:
            CO2 equivalent in kg
        """
        electricity_co2 = kwh * CarbonCalculator.ELECTRICITY_EMISSION
        gas_co2 = gas_m3 * CarbonCalculator.GAS_EMISSION
        return electricity_co2 + gas_co2

    @staticmethod
    def calculate_transport_co2(
        distance_km: float,
        transport_type: str = "car"
    ) -> float:
        """
        Calculate CO2 from transportation
        
        Args:
            distance_km: Distance traveled in km
            transport_type: Type of transport (car, public_transport, bike, walk, flight)
        
        Returns:
            CO2 equivalent in kg
        """
        emission_factor = CarbonCalculator.TRANSPORT_EMISSIONS.get(
            transport_type.lower(), 0.21
        )
        return distance_km * emission_factor

    @staticmethod
    def calculate_diet_co2(diet_type: str, days: int = 1) -> float:
        """
        Calculate daily CO2 from diet
        
        Args:
            diet_type: Type of diet (vegan, vegetarian, mixed, meat_heavy)
            days: Number of days to calculate
        
        Returns:
            CO2 equivalent in kg
        """
        daily_emission = CarbonCalculator.DIET_EMISSIONS.get(
            diet_type.lower(), 4.5
        )
        return daily_emission * days

    @staticmethod
    def calculate_lifestyle_co2(activities: Dict[str, float]) -> float:
        """
        Calculate CO2 from lifestyle activities
        
        Args:
            activities: Dictionary of activity types and counts
                Example: {"shopping": 2, "streaming_hours": 5}
        
        Returns:
            CO2 equivalent in kg
        """
        total_co2 = 0
        
        for activity, quantity in activities.items():
            if activity in CarbonCalculator.LIFESTYLE_ACTIVITIES:
                total_co2 += quantity * CarbonCalculator.LIFESTYLE_ACTIVITIES[activity]
        
        return total_co2

    @staticmethod
    def calculate_daily_footprint(
        energy_kwh: float,
        transport_km: float,
        transport_type: str = "car",
        diet_type: str = "mixed",
        lifestyle_activities: Dict[str, float] = None,
        gas_m3: float = 0
    ) -> Dict[str, float]:
        """
        Calculate complete daily carbon footprint
        
        Returns dictionary with breakdown by category
        """
        if lifestyle_activities is None:
            lifestyle_activities = {}
        
        energy_co2 = CarbonCalculator.calculate_energy_co2(energy_kwh, gas_m3)
        transport_co2 = CarbonCalculator.calculate_transport_co2(
            transport_km, transport_type
        )
        diet_co2 = CarbonCalculator.calculate_diet_co2(diet_type, 1)
        lifestyle_co2 = CarbonCalculator.calculate_lifestyle_co2(lifestyle_activities)
        
        total_co2 = energy_co2 + transport_co2 + diet_co2 + lifestyle_co2
        
        return {
            "energy_co2": round(energy_co2, 2),
            "transport_co2": round(transport_co2, 2),
            "diet_co2": round(diet_co2, 2),
            "lifestyle_co2": round(lifestyle_co2, 2),
            "total_co2": round(total_co2, 2),
            "breakdown": {
                "energy": round(energy_co2, 2),
                "transport": round(transport_co2, 2),
                "diet": round(diet_co2, 2),
                "lifestyle": round(lifestyle_co2, 2),
            }
        }

    @staticmethod
    def get_co2_equivalents() -> Dict[str, float]:
        """
        Get various CO2 equivalents for user context
        
        Returns:
            Dictionary with CO2 equivalents in kg
        """
        return {
            "car_mile": 0.41,  # kg CO2 per mile
            "flight_hour": 90,  # kg CO2 per hour of flight
            "tree_absorbs_annual": 25,  # kg CO2 a tree absorbs per year
            "netflix_hour": 0.036,  # kg CO2 per hour
            "shower_20min": 3.0,  # kg CO2 for a 20-min shower
            "beef_kg": 27,  # kg CO2 per kg of beef
            "chicken_kg": 6.9,  # kg CO2 per kg of chicken
            "vegetables_kg": 2,  # kg CO2 per kg of vegetables
        }

    @staticmethod
    def calculate_reduction_potential(current_footprint: float) -> Dict[str, float]:
        """
        Calculate potential CO2 reductions for different actions
        
        Args:
            current_footprint: Current daily CO2 in kg
        
        Returns:
            Dictionary with potential reductions from different actions
        """
        return {
            "public_transport_vs_car": 0.121 * 20,  # Switching 20 km/day
            "vegetarian_diet": 2.5,  # Daily reduction
            "renewable_energy": 0.4 * 15,  # For 15 kWh daily usage
            "cycling_vs_car": 0.21 * 10,  # Cycling 10 km/day
            "remote_work_day": 0.21 * 50,  # Commute savings (50 km round trip)
            "heating_reduction": 20,  # Lowering temp by 2°C
        }


# Precomputed data for comparisons
GLOBAL_AVERAGES = {
    "uk_annual": 9800,  # kg CO2/person/year
    "us_annual": 16000,  # kg CO2/person/year
    "global_annual": 4500,  # kg CO2/person/year
    "target_2030": 4500,  # kg CO2/person/year (net zero target)
}

CARBON_BENCHMARKS = {
    "low_footprint": 5000,  # kg CO2/year
    "average_footprint": 10000,  # kg CO2/year
    "high_footprint": 15000,  # kg CO2/year
}