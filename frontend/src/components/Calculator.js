import React, { useState } from 'react';
import '../styles/calculator.css';

function Calculator({ onSubmit }) {
  const [formData, setFormData] = useState({
    energy_kwh: '',
    transport_km: '',
    transport_type: 'car',
    diet_type: 'mixed',
    lifestyle_activities: {}
  });

  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const transportTypes = [
    { value: 'car', label: '🚗 Car', emoji: '🚗' },
    { value: 'public_transport', label: '🚌 Public Transport', emoji: '🚌' },
    { value: 'bike', label: '🚴 Bike', emoji: '🚴' },
    { value: 'walk', label: '🚶 Walk', emoji: '🚶' },
    { value: 'flight', label: '✈️ Flight', emoji: '✈️' }
  ];

  const dietTypes = [
    { value: 'vegan', label: '🌱 Vegan', emoji: '🌱' },
    { value: 'vegetarian', label: '🥬 Vegetarian', emoji: '🥬' },
    { value: 'mixed', label: '🍗 Mixed', emoji: '🍗' },
    { value: 'meat_heavy', label: '🥩 Meat Heavy', emoji: '🥩' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLifestyleChange = (activity, value) => {
    setFormData(prev => ({
      ...prev,
      lifestyle_activities: {
        ...prev.lifestyle_activities,
        [activity]: value ? parseFloat(value) : 0
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Validate inputs
    if (!formData.energy_kwh || !formData.transport_km) {
      alert('Please fill in all required fields');
      setLoading(false);
      return;
    }

    try {
      await onSubmit({
        ...formData,
        energy_kwh: parseFloat(formData.energy_kwh),
        transport_km: parseFloat(formData.transport_km)
      });

      setSubmitted(true);
      setTimeout(() => {
        setFormData({
          energy_kwh: '',
          transport_km: '',
          transport_type: 'car',
          diet_type: 'mixed',
          lifestyle_activities: {}
        });
        setSubmitted(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to submit:', error);
      alert('Failed to submit carbon data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator">
      <section className="calc-header">
        <h1>⚙️ Carbon Footprint Calculator</h1>
        <p>Enter your daily activities to calculate your carbon footprint</p>
      </section>

      {submitted && (
        <div className="success-message">
          ✓ Carbon footprint recorded! Dashboard updated.
        </div>
      )}

      <form onSubmit={handleSubmit} className="calculator-form">
        {/* Energy Section */}
        <section className="form-section">
          <h2>⚡ Energy Usage</h2>
          
          <div className="form-group">
            <label htmlFor="energy_kwh">
              Daily Electricity Usage (kWh) *
            </label>
            <input
              type="number"
              id="energy_kwh"
              name="energy_kwh"
              value={formData.energy_kwh}
              onChange={handleInputChange}
              placeholder="e.g., 12"
              step="0.1"
              min="0"
              required
            />
            <small>Average US household: 30 kWh/day</small>
          </div>

          <div className="info-box">
            💡 <strong>Tip:</strong> Check your electricity bill for accurate usage data
          </div>
        </section>

        {/* Transport Section */}
        <section className="form-section">
          <h2>🚗 Transportation</h2>

          <div className="form-group">
            <label htmlFor="transport_km">
              Distance Traveled Today (km) *
            </label>
            <input
              type="number"
              id="transport_km"
              name="transport_km"
              value={formData.transport_km}
              onChange={handleInputChange}
              placeholder="e.g., 20"
              step="0.1"
              min="0"
              required
            />
          </div>

          <div className="form-group">
            <label>Primary Transport Method</label>
            <div className="transport-options">
              {transportTypes.map(type => (
                <label key={type.value} className="option-label">
                  <input
                    type="radio"
                    name="transport_type"
                    value={type.value}
                    checked={formData.transport_type === type.value}
                    onChange={handleInputChange}
                  />
                  <span className="option-text">
                    <span className="emoji">{type.emoji}</span>
                    {type.label.split(' ')[0]}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="info-box">
            🚌 <strong>Eco-Friendly Tip:</strong> Public transport emits 60% less CO₂ than driving alone
          </div>
        </section>

        {/* Diet Section */}
        <section className="form-section">
          <h2>🍽️ Diet</h2>

          <div className="form-group">
            <label>Your Diet Type</label>
            <div className="diet-options">
              {dietTypes.map(type => (
                <label key={type.value} className="option-label">
                  <input
                    type="radio"
                    name="diet_type"
                    value={type.value}
                    checked={formData.diet_type === type.value}
                    onChange={handleInputChange}
                  />
                  <span className="option-text">
                    <span className="emoji">{type.emoji}</span>
                    {type.label.split(' ')[0]}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="info-box">
            🥗 <strong>Did You Know?</strong> Eating vegetarian one day per week saves ~2 kg CO₂
          </div>
        </section>

        {/* Lifestyle Section */}
        <section className="form-section">
          <h2>🛍️ Lifestyle Activities</h2>

          <div className="form-group">
            <label>
              Shopping Trips (count)
              <input
                type="number"
                value={formData.lifestyle_activities['shopping'] || ''}
                onChange={(e) => handleLifestyleChange('shopping', e.target.value)}
                placeholder="0"
                min="0"
                step="1"
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              Streaming/Gaming Hours (count)
              <input
                type="number"
                value={formData.lifestyle_activities['streaming'] || ''}
                onChange={(e) => handleLifestyleChange('streaming', e.target.value)}
                placeholder="0"
                min="0"
                step="0.5"
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              Laundry Cycles (count)
              <input
                type="number"
                value={formData.lifestyle_activities['laundry'] || ''}
                onChange={(e) => handleLifestyleChange('laundry', e.target.value)}
                placeholder="0"
                min="0"
                step="1"
              />
            </label>
          </div>

          <div className="info-box">
            ♻️ <strong>Reduce Impact:</strong> Air-dry clothes instead of using a dryer
          </div>
        </section>

        {/* Submit Button */}
        <div className="form-actions">
          <button
            type="submit"
            className="submit-btn"
            disabled={loading}
          >
            {loading ? 'Recording...' : '📊 Calculate My Footprint'}
          </button>
          <p className="form-note">
            * Required fields. All data is processed locally and securely stored.
          </p>
        </div>
      </form>

      {/* Calculator Info */}
      <section className="calc-info">
        <h2>How It Works</h2>
        <div className="info-grid">
          <div className="info-item">
            <h3>⚡ Energy</h3>
            <p>Based on electricity consumption and grid carbon intensity</p>
          </div>
          <div className="info-item">
            <h3>🚗 Transport</h3>
            <p>Calculated using emission factors for different transport modes</p>
          </div>
          <div className="info-item">
            <h3>🍽️ Diet</h3>
            <p>Based on global average emissions for different diet types</p>
          </div>
          <div className="info-item">
            <h3>🛍️ Lifestyle</h3>
            <p>Includes shopping, entertainment, laundry, and other activities</p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Calculator;