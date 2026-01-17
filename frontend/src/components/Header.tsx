import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageToggle from './LanguageToggle';
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
  batch: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
    </svg>
  ),
  sheets: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M19.5 2h-15A2.5 2.5 0 002 4.5v15A2.5 2.5 0 004.5 22h15a2.5 2.5 0 002.5-2.5v-15A2.5 2.5 0 0019.5 2zM7 6h10v2H7V6zm10 10H7v-2h10v2zm0-4H7v-2h10v2z"/>
    </svg>
  ),
  check: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
};

export default function Header() {
  const location = useLocation();
  const { t } = useLanguage();

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          <div className="flex items-center gap-2">
            <div className="bg-green-500 rounded-full p-1">
              <Icons.check />
            </div>
            <span>{t.header.logo}</span>
          </div>
        </Link>
        
        <nav className="header-nav">
          <Link 
            to="/data-collector" 
            className={`nav-link ${location.pathname === '/data-collector' ? 'active' : ''}`}
          >
            <Icons.chart /> {t.header.dataCollector}
          </Link>
          <Link 
            to="/batch-processing" 
            className={`nav-link ${location.pathname === '/batch-processing' ? 'active' : ''}`}
          >
            <Icons.batch /> Lote
          </Link>
          <Link 
            to="/google-sheets" 
            className={`nav-link ${location.pathname === '/google-sheets' ? 'active' : ''}`}
          >
            <Icons.sheets /> Google Sheets
          </Link>
          <Link 
            to="/chatbot" 
            className={`nav-link ${location.pathname === '/chatbot' ? 'active' : ''}`}
          >
            <Icons.chat /> {t.header.chatbot}
          </Link>
          <Link 
            to="/properties" 
            className={`nav-link ${location.pathname === '/properties' ? 'active' : ''}`}
          >
            <Icons.building /> {t.header.properties}
          </Link>
          <LanguageToggle />
        </nav>
      </div>
    </header>
  );
}
