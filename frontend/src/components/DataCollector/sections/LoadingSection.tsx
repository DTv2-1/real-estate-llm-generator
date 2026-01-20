import React from 'react';
import './LoadingSection.css';

/**
 * Props for LoadingSection component
 */
interface LoadingSectionProps {
  /** Loading message to display */
  message?: string;
  /** Progress percentage (0-100) if available */
  progress?: number;
  /** Array of status messages showing processing steps */
  statusMessages?: string[];
  /** Whether to show animated spinner */
  showSpinner?: boolean;
}

/**
 * Loading section displayed during property processing
 * Shows spinner, progress bar, and status messages
 * 
 * @component
 * @example
 * ```tsx
 * <LoadingSection
 *   message="Procesando propiedad..."
 *   progress={65}
 *   statusMessages={['Descargando contenido...', 'Extrayendo datos...']}
 *   showSpinner={true}
 * />
 * ```
 */
export const LoadingSection: React.FC<LoadingSectionProps> = ({
  message = 'Procesando...',
  progress,
  statusMessages = [],
  showSpinner = true
}) => {
  return (
    <section className="loading-section">
      <div className="loading-container">
        {showSpinner && (
          <div className="loading-spinner">
            <div className="spinner-circle"></div>
          </div>
        )}

        <h3 className="loading-message">{message}</h3>

        {typeof progress === 'number' && (
          <div className="progress-bar-container">
            <div
              className="progress-bar-fill"
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={100}
            />
            <span className="progress-percentage">{Math.round(progress)}%</span>
          </div>
        )}

        {statusMessages.length > 0 && (
          <div className="status-messages">
            {statusMessages.map((msg, index) => (
              <div key={index} className="status-message">
                <span className="status-icon">
                  {index === statusMessages.length - 1 ? '▶' : '✓'}
                </span>
                <span className="status-text">{msg}</span>
              </div>
            ))}
          </div>
        )}

        <div className="loading-tips">
          <p className="tip-text">
            💡 <strong>Tip:</strong> El proceso puede tomar entre 10-30 segundos dependiendo de la complejidad del sitio web.
          </p>
        </div>
      </div>
    </section>
  );
};
