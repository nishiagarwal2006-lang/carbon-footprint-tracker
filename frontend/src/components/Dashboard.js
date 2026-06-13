import React, { useContext, useState, useEffect } from 'react';
import { AppContext } from '../App';
import Charts from './Charts';
import { fetchAPI } from '../utils/api';
import '../styles/dashboard.css';

function Dashboard() {
  const { currentUser, stats, insights, actions } = useContext(AppContext);
  const [monthlyData, setMonthlyData] = useState(null);

  useEffect(() => {
    if (currentUser) {
      loadDashboardStats();
    }
  }, [currentUser]);

  const loadDashboardStats = async () => {
    if (!currentUser) return;
    
    try {
      const statsData = await fetchAPI(`/api/stats/${currentUser.id}?days=30`, 'GET');
      setMonthlyData(statsData);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    }
  };

  if (!stats) {
    return <div className="dashboard loading">Loading dashboard...</div>;
  }

  const getStatusColor = (comparison) => {
    if (comparison < -10) return '#4caf50'; // Green - below average
    if (comparison > 10) return '#f44336'; // Red - above average
    return '#2196f3'; // Blue - average
  };

  const getStatusText = (comparison) => {
    if (comparison < -10) return `${Math.abs(comparison).toFixed(1)}% below global average ✓`;
    if (comparison > 10) return `${comparison.toFixed(1)}% above global average`;
    return 'Close to global average';
  };

  return (
    <div className="dashboard">
      <section className="dashboard-header">
        <h1>🌍 Your Carbon Dashboard</h1>
        <p>Track your progress toward a sustainable lifestyle</p>
      </section>

      {/* Main Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card monthly">
          <h3>Monthly Footprint</h3>
          <div className="stat-value">{stats.total_co2_month?.toFixed(1)} kg</div>
          <p>CO₂ Equivalent</p>
        </div>

        <div className="stat-card saved">
          <h3>CO₂ Saved This Month</h3>
          <div className="stat-value" style={{ color: '#4caf50' }}>
            +{stats.total_co2_saved?.toFixed(1)} kg
          </div>
          <p>From Your Actions</p>
        </div>

        <div className="stat-card average">
          <h3>Daily Average</h3>
          <div className="stat-value">{stats.daily_average?.toFixed(2)} kg</div>
          <p>Per Day</p>
        </div>

        <div className="stat-card comparison">
          <h3>Status</h3>
          <div className="stat-value" style={{ color: getStatusColor(stats.comparison_to_avg) }}>
            {getStatusText(stats.comparison_to_avg)}
          </div>
          <p>vs Global Average</p>
        </div>
      </div>

      {/* Top Emitter */}
      <section className="section">
        <h2>📊 Top Emission Source</h2>
        <div className="top-emitter">
          <div className="emitter-badge">
            {stats.top_emitter_category === 'transport' && '🚗'}
            {stats.top_emitter_category === 'energy' && '⚡'}
            {stats.top_emitter_category === 'diet' && '🍽️'}
            {stats.top_emitter_category === 'lifestyle' && '🛍️'}
            <span>{stats.top_emitter_category}</span>
          </div>
          <p>This is where you emit the most CO₂. Focus here for maximum impact!</p>
        </div>
      </section>

      {/* Charts */}
      {monthlyData && (
        <section className="section">
          <h2>📈 Trends & Breakdown</h2>
          <Charts data={monthlyData} />
        </section>
      )}

      {/* Active Actions */}
      {actions && actions.length > 0 && (
        <section className="section">
          <h2>✅ Your Active Actions ({actions.length})</h2>
          <div className="actions-preview">
            {actions.slice(0, 3).map((action) => (
              <div key={action.id} className="action-item">
                <div className="action-header">
                  <h4>{action.action_name}</h4>
                  <span className="category-badge">{action.category}</span>
                </div>
                <p>Saves {action.co2_saved} kg CO₂ {action.frequency}</p>
                <p className="completions">{action.total_occurrences} times logged</p>
              </div>
            ))}
          </div>
          {actions.length > 3 && (
            <p className="view-more">+{actions.length - 3} more actions</p>
          )}
        </section>
      )}

      {/* Top Insights */}
      {insights && insights.length > 0 && (
        <section className="section">
          <h2>💡 Your Insights</h2>
          <div className="insights-preview">
            {insights.slice(0, 2).map((insight) => (
              <div key={insight.id} className={`insight-card ${insight.priority}`}>
                <div className="insight-header">
                  <h4>{insight.title}</h4>
                  <span className={`priority-badge ${insight.priority}`}>
                    {insight.priority}
                  </span>
                </div>
                <p>{insight.description}</p>
                {insight.co2_impact > 0 && (
                  <p className="impact">
                    Potential impact: {insight.co2_impact.toFixed(1)} kg CO₂
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Call to Action */}
      {actions.length === 0 && (
        <section className="section cta-section">
          <h2>🎯 Get Started</h2>
          <p>No actions tracked yet. Add your first carbon reduction action to start tracking your progress!</p>
        </section>
      )}

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>💚 Every action counts. Together we can make a difference!</p>
      </footer>
    </div>
  );
}

export default Dashboard;