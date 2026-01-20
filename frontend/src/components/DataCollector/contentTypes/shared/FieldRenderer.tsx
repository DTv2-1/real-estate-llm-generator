import React from 'react';

/**
 * Props for FieldRenderer component
 */
interface FieldRendererProps {
  /** Field label */
  label: string;
  /** Field value to render */
  value: string | number | boolean | null | undefined;
  /** Field type for special rendering */
  type?: 'text' | 'url' | 'email' | 'tel' | 'boolean' | 'number' | 'date' | 'currency' | 'list';
  /** Icon to display next to label */
  icon?: string;
  /** Additional CSS class */
  className?: string;
  /** List items if type is 'list' */
  listItems?: string[];
}

/**
 * Generic field renderer for displaying labeled data
 * Handles various data types with appropriate formatting and links
 * 
 * @component
 * @example
 * ```tsx
 * <FieldRenderer
 *   label="Email"
 *   value="contact@example.com"
 *   type="email"
 *   icon="📧"
 * />
 * ```
 */
export const FieldRenderer: React.FC<FieldRendererProps> = ({
  label,
  value,
  type = 'text',
  icon,
  className = '',
  listItems
}) => {
  // Don't render if no value
  if (value === null || value === undefined || value === '') {
    if (type !== 'list' || !listItems || listItems.length === 0) {
      return null;
    }
  }

  const renderValue = () => {
    if (type === 'list' && listItems) {
      return (
        <ul className="field-list">
          {listItems.map((item, index) => (
            <li key={index} className="field-list-item">
              {item}
            </li>
          ))}
        </ul>
      );
    }

    const stringValue = String(value);

    switch (type) {
      case 'url':
        return (
          <a
            href={stringValue}
            target="_blank"
            rel="noopener noreferrer"
            className="field-link"
          >
            {stringValue}
          </a>
        );

      case 'email':
        return (
          <a href={`mailto:${stringValue}`} className="field-link">
            {stringValue}
          </a>
        );

      case 'tel':
        return (
          <a href={`tel:${stringValue}`} className="field-link">
            {stringValue}
          </a>
        );

      case 'boolean':
        return (
          <span className={`field-boolean ${value ? 'true' : 'false'}`}>
            {value ? '✓ Sí' : '✗ No'}
          </span>
        );

      case 'currency':
        return <span className="field-currency">{stringValue}</span>;

      case 'date':
        return <span className="field-date">{stringValue}</span>;

      case 'number':
        return <span className="field-number">{stringValue}</span>;

      default:
        return <span className="field-text">{stringValue}</span>;
    }
  };

  return (
    <div className={`field-renderer ${className}`}>
      <div className="field-label">
        {icon && <span className="field-icon">{icon}</span>}
        <span className="label-text">{label}:</span>
      </div>
      <div className="field-value-container">{renderValue()}</div>
    </div>
  );
};
