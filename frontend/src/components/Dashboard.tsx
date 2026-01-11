import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Icons = {
  home: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  chart: () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <line x1="12" y1="20" x2="12" y2="10"/>
      <line x1="18" y1="20" x2="18" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="16"/>
    </svg>
  ),
  building: () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
      <path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>
    </svg>
  ),
  chat: () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  ),
  check: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  ),
};

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      <div className="dashboard-content">
        <h1 className="dashboard-title">{Icons.home && <Icons.home />} KP Real Estate Platform</h1>
        <p className="dashboard-subtitle">Comprehensive AI-powered real estate management system</p>
        
        <div className="dashboard-cards">
          <div className="dashboard-card" onClick={() => navigate('/data-collector')}>
            <div className="card-icon"><Icons.chart /></div>
            <h2>Data Collector</h2>
            <p>Property collection and management</p>
            <button className="card-button">Access →</button>
          </div>
          
          <div className="dashboard-card" onClick={() => navigate('/properties')}>
            <div className="card-icon"><Icons.building /></div>
            <h2>Properties</h2>
            <p>View indexed properties</p>
            <button className="card-button">Access →</button>
          </div>
          
          <div className="dashboard-card" onClick={() => navigate('/chatbot')}>
            <div className="card-icon"><Icons.chat /></div>
            <h2>AI Chatbot</h2>
            <p>Virtual real estate assistant</p>
            <button className="card-button">Access →</button>
          </div>
        </div>
        
        <div className="dashboard-footer">
          <p>Backend API: <span className="status-indicator"><Icons.check /></span> Connected</p>
        </div>
      </div>
    </div>
  );
}
