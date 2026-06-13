import React from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import '../styles/charts.css';

function Charts({ data }) {
  // Prepare trend data for line chart
  const trendData = data.trend.trend ? data.trend.trend.slice(-14).map((item, idx) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    co2: item.co2,
    energy: item.energy,
    transport: item.transport,
    diet: item.diet,
    lifestyle: item.lifestyle
  })) : [];

  // Prepare breakdown data for pie chart
  const breakdownData = data.monthly_stats.breakdown ? [
    { name: 'Energy', value: data.monthly_stats.breakdown.energy },
    { name: 'Transport', value: data.monthly_stats.breakdown.transport },
    { name: 'Diet', value: data.monthly_stats.breakdown.diet },
    { name: 'Lifestyle', value: data.monthly_stats.breakdown.lifestyle }
  ].filter(item => item.value > 0) : [];

  const COLORS = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'];

  const formatNumber = (value) => {
    return value.toFixed(1);
  };

  return (
    <div className="charts-container">
      {/* Trend Line Chart */}
      <div className="chart-card">
        <h3>📈 Daily Trend (Last 14 Days)</h3>
        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
              <YAxis label={{ value: 'CO₂ (kg)', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                formatter={(value) => formatNumber(value)}
                contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', color: '#fff' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="co2"
                stroke="#FF6B6B"
                dot={{ fill: '#FF6B6B', r: 4 }}
                activeDot={{ r: 6 }}
                name="Total CO₂"
              />
              <Line
                type="monotone"
                dataKey="transport"
                stroke="#4ECDC4"
                dot={false}
                name="Transport"
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="no-data">No trend data available yet.</p>
        )}
      </div>

      {/* Breakdown Pie Chart */}
      <div className="chart-card">
        <h3>🥧 Emission Breakdown</h3>
        {breakdownData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={breakdownData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value.toFixed(1)} kg`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {breakdownData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatNumber(value) + ' kg'} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="no-data">No breakdown data available yet.</p>
        )}
      </div>

      {/* Category Breakdown Bar Chart */}
      <div className="chart-card wide">
        <h3>📊 Emission by Category (Monthly)</h3>
        {breakdownData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={breakdownData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'CO₂ (kg)', angle: -90, position: 'insideLeft' }} />
              <Tooltip formatter={(value) => formatNumber(value) + ' kg'} />
              <Bar dataKey="value" fill="#82ca9d" name="CO₂ Emissions" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="no-data">No category data available yet.</p>
        )}
      </div>

      {/* Statistics Cards */}
      <div className="stats-summary">
        <div className="summary-card">
          <h4>Total This Month</h4>
          <p className="big-number">
            {data.monthly_stats.total_co2?.toFixed(1)} kg
          </p>
          <p className="subtitle">CO₂ Equivalent</p>
        </div>

        <div className="summary-card">
          <h4>Daily Average</h4>
          <p className="big-number">
            {data.monthly_stats.daily_average?.toFixed(2)} kg
          </p>
          <p className="subtitle">Per Day</p>
        </div>

        <div className="summary-card">
          <h4>Days Tracked</h4>
          <p className="big-number">
            {data.monthly_stats.days_tracked}
          </p>
          <p className="subtitle">Days</p>
        </div>

        <div className="summary-card">
          <h4>Trend</h4>
          <p className="big-number trend">
            {data.monthly_stats.trend === 'improving' ? '📉' :
             data.monthly_stats.trend === 'worsening' ? '📈' : '➡️'}
          </p>
          <p className="subtitle">{data.monthly_stats.trend}</p>
        </div>
      </div>

      {/* Comparison Information */}
      <div className="chart-card comparison-info">
        <h3>🌍 Your Comparison</h3>
        <div className="comparison-details">
          <div className="comparison-item">
            <p>Global Average (Annual)</p>
            <p className="value">4,500 kg</p>
          </div>
          <div className="comparison-item">
            <p>Your Projection (Annual)</p>
            <p className="value">
              {(data.monthly_stats.total_co2 * 12).toFixed(0)} kg
            </p>
          </div>
          <div className="comparison-item">
            <p>Difference</p>
            <p className={`value ${data.comparison?.status === 'below_average' ? 'positive' : 'negative'}`}>
              {data.comparison?.comparison_to_global?.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Charts;