import React, { useState, useContext } from 'react';
import { AppContext } from '../App';
import { fetchAPI } from '../utils/api';
import '../styles/actions.css';

function ActionTracker({ onAddAction }) {
  const { actions } = useContext(AppContext);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    action_name: '',
    category: 'transport',
    co2_saved: '',
    frequency: 'weekly'
  });
  const [loading, setLoading] = useState(false);

  const categories = [
    { value: 'transport', label: '🚗 Transport', examples: 'Walk, bike, carpooling' },
    { value: 'energy', label: '⚡ Energy', examples: 'Solar, LED bulbs, thermostat' },
    { value: 'diet', label: '🍽️ Diet', examples: 'Vegetarian meals, local food' },
    { value: 'lifestyle', label: '🛍️ Lifestyle', examples: 'Reduce shopping, recycling' }
  ];

  const frequencies = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' }
  ];

  const predefinedActions = {
    transport: [
      { name: 'Use public transport', co2_saved: 2.4 },
      { name: 'Bike to work/school', co2_saved: 4.2 },
      { name: 'Carpool', co2_saved: 1.8 },
      { name: 'Work from home', co2_saved: 10.5 }
    ],
    energy: [
      { name: 'Switch to LED bulbs', co2_saved: 0.5 },
      { name: 'Use renewable energy', co2_saved: 2.0 },
      { name: 'Optimize heating/cooling', co2_saved: 1.5 },
      { name: 'Unplug devices', co2_saved: 0.3 }
    ],
    diet: [
      { name: 'Meatless Monday', co2_saved: 2.0 },
      { name: 'Go vegetarian', co2_saved: 2.5 },
      { name: 'Buy local food', co2_saved: 0.8 },
      { name: 'Reduce food waste', co2_saved: 1.2 }
    ],
    lifestyle: [
      { name: 'Reduce shopping', co2_saved: 1.0 },
      { name: 'Recycle more', co2_saved: 0.5 },
      { name: 'Buy secondhand', co2_saved: 3.0 },
      { name: 'Reduce water usage', co2_saved: 0.3 }
    ]
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddPredefined = (action) => {
    setFormData(prev => ({
      ...prev,
      action_name: action.name,
      co2_saved: action.co2_saved.toString()
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.action_name || !formData.co2_saved) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      await onAddAction({
        ...formData,
        co2_saved: parseFloat(formData.co2_saved)
      });

      // Reset form
      setFormData({
        action_name: '',
        category: 'transport',
        co2_saved: '',
        frequency: 'weekly'
      });
      setShowForm(false);
    } catch (error) {
      console.error('Failed to add action:', error);
      alert('Failed to add action. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAction = async (actionId, occurrences) => {
    try {
      await fetchAPI(`/api/actions/${actionId}`, 'PUT', {
        total_occurrences: occurrences
      });
      
      // Reload dashboard data
      // This would typically trigger a refresh of the actions list
    } catch (error) {
      console.error('Failed to update action:', error);
    }
  };

  const handleDeleteAction = async (actionId) => {
    if (window.confirm('Are you sure you want to deactivate this action?')) {
      try {
        await fetchAPI(`/api/actions/${actionId}`, 'DELETE');
      } catch (error) {
        console.error('Failed to delete action:', error);
      }
    }
  };

  return (
    <div className="action-tracker">
      <section className="tracker-header">
        <h1>✅ Action Tracker</h1>
        <p>Log your carbon reduction actions and track your progress</p>
      </section>

      {/* Add Action Button */}
      {!showForm && (
        <button 
          className="add-action-btn"
          onClick={() => setShowForm(true)}
        >
          ➕ Add New Action
        </button>
      )}

      {/* Add Action Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="action-form">
          <h2>Add Carbon Reduction Action</h2>

          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleInputChange}
              required
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Quick Action Selection */}
          {formData.category && (
            <div className="quick-actions">
              <p>Quick actions:</p>
              <div className="quick-actions-list">
                {predefinedActions[formData.category].map((action, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="quick-action-btn"
                    onClick={() => handleAddPredefined(action)}
                  >
                    {action.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="action_name">Action Name *</label>
            <input
              type="text"
              id="action_name"
              name="action_name"
              value={formData.action_name}
              onChange={handleInputChange}
              placeholder="e.g., Use public transport twice a week"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="co2_saved">CO₂ Saved per Occurrence (kg) *</label>
            <input
              type="number"
              id="co2_saved"
              name="co2_saved"
              value={formData.co2_saved}
              onChange={handleInputChange}
              placeholder="e.g., 2.4"
              step="0.1"
              min="0"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="frequency">Frequency</label>
            <select
              id="frequency"
              name="frequency"
              value={formData.frequency}
              onChange={handleInputChange}
              required
            >
              {frequencies.map(freq => (
                <option key={freq.value} value={freq.value}>
                  {freq.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Adding...' : '✓ Add Action'}
            </button>
            <button
              type="button"
              className="cancel-btn"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Current Actions List */}
      <section className="actions-section">
        <h2>Your Active Actions</h2>
        
        {actions && actions.length > 0 ? (
          <div className="actions-list">
            {actions.map(action => (
              <div key={action.id} className="action-card">
                <div className="action-content">
                  <div className="action-title">
                    <h3>{action.action_name}</h3>
                    <span className="category-badge">{action.category}</span>
                  </div>
                  
                  <div className="action-stats">
                    <span className="stat">
                      💚 {action.co2_saved} kg CO₂ {action.frequency}
                    </span>
                    <span className="stat">
                      ✓ Logged {action.total_occurrences} times
                    </span>
                  </div>

                  <div className="action-progress">
                    <p>This month projection:</p>
                    <p className="projection">
                      {(action.co2_saved * 
                        (action.frequency === 'daily' ? 30 : 
                         action.frequency === 'weekly' ? 4 : 1)).toFixed(1)} kg saved
                    </p>
                  </div>
                </div>

                <div className="action-controls">
                  <button
                    className="log-btn"
                    onClick={() => handleUpdateAction(action.id, action.total_occurrences + 1)}
                    title="Log this action"
                  >
                    ✓
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteAction(action.id)}
                    title="Deactivate this action"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No actions yet. Start by adding your first carbon reduction action!</p>
          </div>
        )}
      </section>

      {/* Tips Section */}
      <section className="tips-section">
        <h2>💡 Action Ideas by Category</h2>
        <div className="tips-grid">
          <div className="tip-card">
            <h3>🚗 Transportation</h3>
            <ul>
              <li>Use public transport 2-3x/week</li>
              <li>Bike or walk for short trips</li>
              <li>Carpool with colleagues</li>
              <li>Work from home when possible</li>
            </ul>
          </div>

          <div className="tip-card">
            <h3>⚡ Energy</h3>
            <ul>
              <li>Switch to LED bulbs</li>
              <li>Adjust thermostat by 2°C</li>
              <li>Use renewable energy</li>
              <li>Unplug devices when not in use</li>
            </ul>
          </div>

          <div className="tip-card">
            <h3>🍽️ Diet</h3>
            <ul>
              <li>Go vegetarian one day/week</li>
              <li>Buy local produce</li>
              <li>Reduce food waste</li>
              <li>Eat seasonal foods</li>
            </ul>
          </div>

          <div className="tip-card">
            <h3>🛍️ Lifestyle</h3>
            <ul>
              <li>Buy secondhand items</li>
              <li>Reduce shopping frequency</li>
              <li>Recycle properly</li>
              <li>Use reusable bags/containers</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

export default ActionTracker;