import React from 'react';

/**
 * Props for SectionCard component
 */
interface SectionCardProps {
  /** Section title */
  title: string;
  /** Icon to display in header */
  icon?: string;
  /** Child content to render inside the card */
  children: React.ReactNode;
  /** Whether the section is collapsible */
  collapsible?: boolean;
  /** Initial collapsed state (if collapsible) */
  defaultCollapsed?: boolean;
  /** Additional CSS class */
  className?: string;
}

/**
 * Reusable card component for organizing content sections
 * Supports collapsible behavior for better space management
 * 
 * @component
 * @example
 * ```tsx
 * <SectionCard
 *   title="Detalles de la Propiedad"
 *   icon="🏠"
 *   collapsible={true}
 * >
 *   <FieldRenderer label="Tipo" value="Casa" />
 *   <FieldRenderer label="Habitaciones" value={3} />
 * </SectionCard>
 * ```
 */
export const SectionCard: React.FC<SectionCardProps> = ({
  title,
  icon,
  children,
  collapsible = false,
  defaultCollapsed = false,
  className = ''
}) => {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);

  const toggleCollapse = () => {
    if (collapsible) {
      setIsCollapsed(!isCollapsed);
    }
  };

  return (
    <div className={`section-card ${className} ${isCollapsed ? 'collapsed' : ''}`}>
      <div
        className={`section-header ${collapsible ? 'clickable' : ''}`}
        onClick={toggleCollapse}
        role={collapsible ? 'button' : undefined}
        tabIndex={collapsible ? 0 : undefined}
        onKeyPress={(e) => {
          if (collapsible && (e.key === 'Enter' || e.key === ' ')) {
            toggleCollapse();
          }
        }}
      >
        {icon && <span className="section-icon">{icon}</span>}
        <h3 className="section-title">{title}</h3>
        {collapsible && (
          <span className="collapse-indicator">
            {isCollapsed ? '▶' : '▼'}
          </span>
        )}
      </div>

      {!isCollapsed && <div className="section-content">{children}</div>}
    </div>
  );
};
