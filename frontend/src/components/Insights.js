import React, { useContext, useState, useEffect } from 'react';
import { AppContext } from '../App';
import { fetchAPI } from '../utils/api';
import '../styles/insights.css';

function Insights() {
  const { currentUser, insights, loadDashboardData } = useContext(AppContext);
  const [allInsights, setAllInsights] = useState(insights || []);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    setAllInsights(insights || []);
  }, [insights]);

  const generateNewInsights = async () => {
    if (!currentUser) return;

    setLoading(true);
    try {
      await fetchAPI(`/api/insights/generate/${currentUser.id}`, 'POST');
      await loadDashboardData(currentUser.id);
    } catch (error) {
      console.error('Failed to generate insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (insightId) => {
    try {
      await fetchAPI(`/api/insights/${insightId}/read`, 'PUT');
      setAllInsights(allInsights.map(insight => 
        insight.id === insightId ? { ...insight, is_read: true } : insight
      ));
    } catch (error) {
      console.error('Failed to mark insight as read:', error);
    }
  };

  const filteredInsights = filter === 'all' 
    ? allInsights 
    : allInsights.filter(insight => insight.category === filter);

  const getCategoryIcon = (category) => {
    const icons = {
      recommendation: '💡',
      milestone: '🎉',
      warning: '⚠️',
      opportunity: '🎯'
    };
    return icons[category] || '✨';
  };

  const getCategoryLabel = (category) => {
    const labels = {
      recommendation: 'Recommendation',
      milestone: 'Milestone',
      warning: 'Warning',
      opportunity: 'Opportunity'
    };
    return labels[category] || category;
  };

  return (
    <div className="insights">
      <section className="insights-header">
        <h1>💡 Your Personalized Insights</h1>
        <p>AI-generated recommendations based on your carbon footprint</p>
      </section>

      {/* Actions */}
      <div className="insights-actions">
        <button
          className="refresh-btn"
          onClick={generateNewInsights}
          disabled={loading}
        >
          {loading ? '🔄 Generating...' : '🔄 Generate New Insights'}
        </button>

        {/* Filter */}
        <div className="filter-group">
          <label htmlFor="insight-filter">Filter by type:</label>
          <select
            id="insight-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="recommendation">💡 Recommendations</option>
            <option value="milestone">🎉 Milestones</option>
            <option value="warning">⚠️ Warnings</option>
            <option value="opportunity">🎯 Opportunities</option>
          </select>
        </div>
      </div>

      {/* Insights List */}
      {filteredInsights.length > 0 ? (
        <div className="insights-grid">
          {filteredInsights.map(insight => (
            <div
              key={insight.id}
              className={`insight-card ${insight.category} ${insight.priority} ${insight.is_read ? 'read' : 'unread'}`}
              onClick={() => !insight.is_read && markAsRead(insight.id)}
            >
              <div className="insight-header">
                <div className="header-content">
                  <span className="icon">{getCategoryIcon(insight.category)}</span>
                  <div>
                    <h3>{insight.title}</h3>
                    <span className="category-label">
                      {getCategoryLabel(insight.category)}
                    </span>
                  </div>
                </div>
                <span className={`priority-badge ${insight.priority}`}>
                  {insight.priority.toUpperCase()}
                </span>
              </div>

              <p className="description">{insight.description}</p>

              {insight.co2_impact > 0 && (
                <div className="impact-indicator">
                  <span className="impact-label">Potential Impact:</span>
                  <span className="impact-value">
                    {insight.co2_impact.toFixed(2)} kg CO₂
                  </span>
                </div>
              )}

              {!insight.is_read && (
                <div className="unread-indicator">New</div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <p>No insights available yet.</p>
          <p>Start tracking your carbon footprint to get personalized insights!</p>
          <button
            className="primary-btn"
            onClick={generateNewInsights}
            disabled={loading}
          >
            Generate Insights
          </button>
        </div>
      )}

      {/* Insight Categories Explanation */}
      <section className="insight-guide">
        <h2>Understanding Your Insights</h2>
        <div className="guide-grid">
          <div className="guide-item">
            <h3>💡 Recommendations</h3>
            <p>Personalized suggestions to reduce your carbon footprint based on your activities.</p>
          </div>

          <div className="guide-item">
            <h3>🎉 Milestones</h3>
            <p>Celebrate your achievements! These mark significant progress in your sustainability journey.</p>
          </div>

          <div className="guide-item">
            <h3>⚠️ Warnings</h3>
            <p>Areas where your emissions are increasing. Take action to reverse the trend.</p>
          </div>

          <div className="guide-item">
            <h3>🎯 Opportunities</h3>
            <p>High-impact actions you can take to significantly reduce your carbon footprint.</p>
          </div>
        </div>
      </section>

      {/* Priority Explanation */}
      <section className="priority-guide">
        <h2>Priority Levels</h2>
        <div className="priority-items">
          <div className="priority-item high">
            <strong>🔴 High Priority</strong> - Take immediate action
          </div>
          <div className="priority-item medium">
            <strong>🟡 Medium Priority</strong> - Important but not urgent
          </div>
          <div className="priority-item low">
            <strong>🟢 Low Priority</strong> - Nice to have
          </div>
        </div>
      </section>
    </div>
  );
}

export default Insights;