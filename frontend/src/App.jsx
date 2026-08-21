import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Link } from 'react-router-dom';
import {
  Home,
  UploadCloud,
  History as HistoryIcon,
  BarChart2,
  List,
  Settings,
  Menu,
  X,
  Moon,
  Bell,
  ChevronDown,
} from 'lucide-react';
import './App.css';

// Pages
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import ReportViewer from './pages/ReportViewer';
import History from './pages/History';
import AgentLogs from './pages/AgentLogs';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className={`app-shell${sidebarOpen ? '' : ' sidebar-collapsed'}`}>
        <aside className="sidebar">
          <div className="sidebar-header">
            <Link to="/" className="sidebar-brand">
              <div className="brand-icon">
                <div className="brand-dot"></div>
                <div className="brand-dot"></div>
                <div className="brand-dot"></div>
              </div>
              <span className="brand-title">
                DataInsight AI
                <span className="brand-subtitle">Multi-Agent Platform</span>
              </span>
            </Link>
          </div>

          <nav className="sidebar-nav" aria-label="Primary navigation">
            <NavLink to="/" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`} end>
              <Home size={18} className="sidebar-link-icon" />
              <span>Dashboard</span>
            </NavLink>
            <NavLink to="/upload" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
              <UploadCloud size={18} className="sidebar-link-icon" />
              <span>Upload Dataset</span>
            </NavLink>
            <NavLink to="/history" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
              <HistoryIcon size={18} className="sidebar-link-icon" />
              <span>History</span>
            </NavLink>

            <NavLink to="/agent-logs" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
              <List size={18} className="sidebar-link-icon" />
              <span>Agent Logs</span>
            </NavLink>
            <button type="button" className="sidebar-link sidebar-link-muted">
              <Settings size={18} className="sidebar-link-icon" />
              <span>Settings</span>
            </button>
          </nav>

          <div className="sidebar-card">
            <div className="ai-stars">✨</div>
            <div className="ai-content">
              <strong>AI Powered Insights</strong>
              <p>Get intelligent insights and detect bias in your datasets using multi-agent AI.</p>
            </div>
          </div>
        </aside>

        <div className="app-content">
          <header className="topbar">
            <div className="topbar-left">
              <button
                type="button"
                className="menu-button"
                aria-label={sidebarOpen ? 'Close navigation' : 'Open navigation'}
                onClick={() => setSidebarOpen(prev => !prev)}
              >
                {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
              <h1 className="topbar-title">Dashboard</h1>
            </div>

            <div className="topbar-actions">
              <Link to="/upload" className="btn btn-primary btn-upload">
                <span className="plus-icon">+</span> Upload Dataset
              </Link>
              <button type="button" className="icon-button" aria-label="Toggle theme">
                <Moon size={20} />
              </button>
              <button type="button" className="icon-button icon-button-notification" aria-label="Notifications">
                <Bell size={20} />
                <span className="notification-badge">3</span>
              </button>
              <button type="button" className="profile-chip" aria-label="Admin profile">
                <div className="profile-avatar">A</div>
                <span className="profile-name">Admin</span>
                <ChevronDown size={14} className="profile-caret" />
              </button>
            </div>
          </header>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/report/:id" element={<ReportViewer />} />
              <Route path="/history" element={<History />} />
              <Route path="/reports" element={<History />} />
              <Route path="/agent-logs" element={<AgentLogs />} />
            </Routes>
          </main>

          <footer className="app-footer">
            <span>© 2024 DataInsight AI Platform. All rights reserved.</span>
            <span>Version 1.0.0</span>
          </footer>
        </div>
      </div>
    </Router>
  );
}

export default App;
