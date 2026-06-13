import React, { useState, useEffect, createContext } from 'react';
import './App.css';
import Header from './components/Header';
import Calculator from './components/Calculator';
import Dashboard from './components/Dashboard';
import ActionTracker from './components/ActionTracker';
import Insights from './components/Insights';
import { fetchAPI } from './utils/api';

// Create context for app state
export const AppContext = createContext();

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('en');
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [insights, setInsights] = useState([]);
  const [actions, setActions] = useState([]);

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // Set language
  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const initializeApp = async () => {
    setLoading(true);
    try {
      // Get or create user
      const savedUserId = localStorage.getItem('userId');
      
      if (savedUserId) {
        await loadUserData(parseInt(savedUserId));
      } else {
        // Create new user
        const newUser = await createNewUser();
        if (newUser) {
          localStorage.setItem('userId', newUser.id);
          setCurrentUser(newUser);
        }
      }
    } catch (error) {
      console.error('Failed to initialize app:', error);
    } finally {
      setLoading(false);
    }
  };

  const createNewUser = async () => {
    try {
      const timestamp = Date.now();
      const response = await fetchAPI('/api/users', 'POST', {
        username: `user_${timestamp}`,
        email: `user${timestamp}@example.com`,
        language: language
      });
      return response;
    } catch (error) {
      console.error('Failed to create user:', error);
      return null;
    }
  };

  const loadUserData = async (userId) => {
    try {
      const user = await fetchAPI(`/api/users/${userId}`, 'GET');
      setCurrentUser(user);
      
      // Load stats and insights
      await loadDashboardData(userId);
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const loadDashboardData = async (userId) => {
    try {
      const dashboardData = await fetchAPI(`/api/dashboard/${userId}`, 'GET');
      setStats(dashboardData.current_stats);
      setInsights(dashboardData.insights);
      setActions(dashboardData.actions);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleAddFootprint = async (footprintData) => {
    if (!currentUser) return;
    
    try {
      setLoading(true);
      await fetchAPI(`/api/carbon-footprint/${currentUser.id}`, 'POST', footprintData);
      
      // Reload dashboard data
      await loadDashboardData(currentUser.id);
      
      // Generate new insights
      await fetchAPI(`/api/insights/generate/${currentUser.id}`, 'POST');
      await loadDashboardData(currentUser.id);
      
      setCurrentPage('dashboard');
    } catch (error) {
      console.error('Failed to add footprint:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAction = async (actionData) => {
    if (!currentUser) return;
    
    try {
      setLoading(true);
      await fetchAPI(`/api/actions/${currentUser.id}`, 'POST', actionData);
      
      // Reload actions
      await loadDashboardData(currentUser.id);
    } catch (error) {
      console.error('Failed to add action:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleLanguageChange = async (lang) => {
    setLanguage(lang);
    
    if (currentUser) {
      try {
        await fetchAPI(`/api/users/${currentUser.id}`, 'PUT', {
          language: lang,
          dark_mode: darkMode
        });
      } catch (error) {
        console.error('Failed to update language preference:', error);
      }
    }
  };

  if (loading && !currentUser) {
    return (
      <div className="app loading-screen">
        <div className="spinner"></div>
        <p>Loading Carbon Footprint Tracker...</p>
      </div>
    );
  }

  return (
    <AppContext.Provider value={{
      currentUser,
      darkMode,
      language,
      stats,
      insights,
      actions,
      loading,
      onAddFootprint: handleAddFootprint,
      onAddAction: handleAddAction,
      onToggleDarkMode: handleToggleDarkMode,
      onLanguageChange: handleLanguageChange,
      loadDashboardData
    }}>
      <div className={`app ${darkMode ? 'dark-mode' : 'light-mode'}`}>
        <Header 
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          onToggleDarkMode={handleToggleDarkMode}
          onLanguageChange={handleLanguageChange}
        />
        
        <main className="main-content">
          {currentPage === 'dashboard' && <Dashboard />}
          {currentPage === 'calculator' && <Calculator onSubmit={handleAddFootprint} />}
          {currentPage === 'actions' && <ActionTracker onAddAction={handleAddAction} />}
          {currentPage === 'insights' && <Insights />}
        </main>

        {loading && <div className="loading-overlay"></div>}
      </div>
    </AppContext.Provider>
  );
}

export default App;