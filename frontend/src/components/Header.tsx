import { Link, useLocation } from 'react-router-dom';
import './Header.css';

const Icons = {
  home: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  chart: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="12" y1="20" x2="12" y2="10"/>
      <line x1="18" y1="20" x2="18" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="16"/>
    </svg>
  ),
  chat: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  ),
  building: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
      <path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>
    </svg>
  ),
};

export default function Header() {
  const location = useLocation();

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          {Icons.home && <Icons.home />} Real Estate LLM
        </Link>
        
        <nav className="header-nav">
          <Link 
            to="/data-collector" 
            className={`nav-link ${location.pathname === '/data-collector' ? 'active' : ''}`}
          >
            <Icons.chart /> Data Collector
          </Link>
          <Link 
            to="/chatbot" 
            className={`nav-link ${location.pathname === '/chatbot' ? 'active' : ''}`}
          >
            <Icons.chat /> Chatbot
          </Link>
          <Link 
            to="/properties" 
            className={`nav-link ${location.pathname === '/properties' ? 'active' : ''}`}
          >
            <Icons.building /> Properties
          </Link>
        </nav>
      </div>
    </header>
  );
}
