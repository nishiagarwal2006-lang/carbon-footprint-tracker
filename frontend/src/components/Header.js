import React from 'react';
import '../styles/header.css';

function Header({ currentPage, onPageChange, onToggleDarkMode, onLanguageChange }) {
  const pages = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'calculator', label: 'Calculator', icon: '⚙️' },
    { id: 'actions', label: 'Actions', icon: '✅' },
    { id: 'insights', label: 'Insights', icon: '💡' }
  ];

  return (
    <header className="app-header">
      <div className="header-content">
        {/* Logo */}
        <div className="logo">
          <h1>🌍 Carbon Tracker</h1>
          <p>Track • Reduce • Sustain</p>
        </div>

        {/* Navigation */}
        <nav className="main-nav">
          {pages.map(page => (
            <button
              key={page.id}
              className={`nav-btn ${currentPage === page.id ? 'active' : ''}`}
              onClick={() => onPageChange(page.id)}
              title={page.label}
            >
              <span className="nav-icon">{page.icon}</span>
              <span className="nav-label">{page.label}</span>
            </button>
          ))}
        </nav>

        {/* Controls */}
        <div className="header-controls">
          {/* Language Selector */}
          <select
            className="language-select"
            onChange={(e) => onLanguageChange(e.target.value)}
            title="Select Language"
          >
            <option value="en">🇬🇧 English</option>
            <option value="es">🇪🇸 Español</option>
            <option value="fr">🇫🇷 Français</option>
            <option value="de">🇩🇪 Deutsch</option>
          </select>

          {/* Dark Mode Toggle */}
          <button
            className="dark-mode-toggle"
            onClick={onToggleDarkMode}
            title="Toggle dark mode"
            aria-label="Toggle dark mode"
          >
            🌙
          </button>
        </div>
      </div>

      {/* Mobile Menu Indicator */}
      <div className="mobile-nav-indicator">
        <p>📱 Use desktop for best experience</p>
      </div>
    </header>
  );
}

export default Header;