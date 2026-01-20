import React from 'react';
import './Header.css';

/**
 * Props for the Header component
 */
interface HeaderProps {
  /** Daily statistics count */
  dailyCount: number;
  /** Tutorial state */
  tutorial: {
    isActive: boolean;
    currentStep: number;
  };
  /** Handler to start tutorial */
  onStartTutorial: () => void;
  /** Handler to close tutorial */
  onCloseTutorial: () => void;
}

/**
 * Header component with title, stats counter, and tutorial button
 * Displays the main navigation area of the DataCollector
 * 
 * @component
 * @example
 * ```tsx
 * <Header
 *   dailyCount={42}
 *   tutorial={{ isActive: false, currentStep: 0 }}
 *   onStartTutorial={handleStartTutorial}
 *   onCloseTutorial={handleCloseTutorial}
 * />
 * ```
 */
export const Header: React.FC<HeaderProps> = ({
  dailyCount,
  tutorial,
  onStartTutorial,
  onCloseTutorial
}) => {
  return (
    <header className="data-collector-header">
      <div className="header-content">
        <h1 className="header-title">🏠 Recolector de Propiedades</h1>
        
        <div className="header-actions">
          <DailyStatsCounter count={dailyCount} />
          
          <button
            onClick={tutorial.isActive ? onCloseTutorial : onStartTutorial}
            className="tutorial-button"
            aria-label={tutorial.isActive ? 'Cerrar tutorial' : 'Iniciar tutorial'}
          >
            {tutorial.isActive ? '✕ Cerrar Tutorial' : '❓ Tutorial'}
          </button>
        </div>
      </div>
    </header>
  );
};

/**
 * Props for the DailyStatsCounter component
 */
interface DailyStatsCounterProps {
  /** Number of properties ingested today */
  count: number;
}

/**
 * Displays the daily ingestion count with visual indicator
 * Shows a badge with the number of properties processed today
 * 
 * @component
 */
export const DailyStatsCounter: React.FC<DailyStatsCounterProps> = ({ count }) => {
  return (
    <div className="daily-stats-counter" title={`${count} propiedades ingresadas hoy`}>
      <span className="stats-icon">📊</span>
      <span className="stats-label">Hoy:</span>
      <span className="stats-count">{count}</span>
    </div>
  );
};
