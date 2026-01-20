import React from 'react';
import './Sidebar.css';
import type { PropertyData } from '../types';

/**
 * Props for the Sidebar component
 */
interface SidebarProps {
  /** Flag indicating if sidebar is collapsed */
  isCollapsed: boolean;
  /** Handler to toggle sidebar state */
  onToggle: () => void;
  /** Array of recent properties grouped by category */
  propertiesByCategory: Record<string, PropertyData[]>;
  /** Handler when a property is selected from history */
  onSelectProperty: (property: PropertyData) => void;
  /** Currently selected property ID (if any) */
  selectedPropertyId?: string;
}

/**
 * Sidebar component with collapsible property history
 * Displays recent properties organized by category
 * 
 * @component
 * @example
 * ```tsx
 * <Sidebar
 *   isCollapsed={false}
 *   onToggle={handleToggle}
 *   propertiesByCategory={groupedProperties}
 *   onSelectProperty={handleSelect}
 *   selectedPropertyId="123"
 * />
 * ```
 */
export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggle,
  propertiesByCategory,
  onSelectProperty,
  selectedPropertyId
}) => {
  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <button
        className="sidebar-toggle"
        onClick={onToggle}
        aria-label={isCollapsed ? 'Expandir historial' : 'Colapsar historial'}
      >
        {isCollapsed ? '▶' : '◀'}
      </button>

      {!isCollapsed && (
        <div className="sidebar-content">
          <h2 className="sidebar-title">📚 Historial de Contenidos</h2>
          <PropertyHistoryList
            propertiesByCategory={propertiesByCategory}
            onSelectProperty={onSelectProperty}
            selectedPropertyId={selectedPropertyId}
          />
        </div>
      )}
    </aside>
  );
};

/**
 * Props for PropertyHistoryList component
 */
interface PropertyHistoryListProps {
  /** Properties grouped by category */
  propertiesByCategory: Record<string, PropertyData[]>;
  /** Handler when property is selected */
  onSelectProperty: (property: PropertyData) => void;
  /** Currently selected property ID */
  selectedPropertyId?: string;
}

/**
 * List of properties organized by category groups
 * Each category can be expanded/collapsed independently
 * 
 * @component
 */
export const PropertyHistoryList: React.FC<PropertyHistoryListProps> = ({
  propertiesByCategory,
  onSelectProperty,
  selectedPropertyId
}) => {
  const [expandedCategories, setExpandedCategories] = React.useState<Set<string>>(
    new Set(Object.keys(propertiesByCategory))
  );

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  return (
    <div className="property-history-list">
      {Object.entries(propertiesByCategory).map(([category, properties]) => (
        <CategoryGroup
          key={category}
          category={category}
          properties={properties}
          isExpanded={expandedCategories.has(category)}
          onToggle={() => toggleCategory(category)}
          onSelectProperty={onSelectProperty}
          selectedPropertyId={selectedPropertyId}
        />
      ))}
    </div>
  );
};

/**
 * Props for CategoryGroup component
 */
interface CategoryGroupProps {
  /** Category name */
  category: string;
  /** Properties in this category */
  properties: PropertyData[];
  /** Whether category is expanded */
  isExpanded: boolean;
  /** Handler to toggle expansion */
  onToggle: () => void;
  /** Handler when property is selected */
  onSelectProperty: (property: PropertyData) => void;
  /** Currently selected property ID */
  selectedPropertyId?: string;
}

/**
 * Collapsible group of properties for a single category
 * Shows category name, count badge, and list of properties
 * 
 * @component
 */
export const CategoryGroup: React.FC<CategoryGroupProps> = ({
  category,
  properties,
  isExpanded,
  onToggle,
  onSelectProperty,
  selectedPropertyId
}) => {
  return (
    <div className="category-group">
      <button
        className="category-header"
        onClick={onToggle}
        aria-expanded={isExpanded}
      >
        <span className="category-icon">{isExpanded ? '▼' : '▶'}</span>
        <span className="category-name">{category}</span>
        <span className="category-count">{properties.length}</span>
      </button>

      {isExpanded && (
        <ul className="category-properties">
          {properties.map((property, index) => {
            const contentTypeLabel = property.content_type || 'Contenido';
            const displayTitle = property.title || property.name || 'Sin título';
            const urlDomain = property.url ? new URL(property.url).hostname.replace('www.', '') : '';
            
            return (
              <li
                key={property.id || index}
                className={`property-item ${property.id === selectedPropertyId ? 'selected' : ''}`}
                onClick={() => onSelectProperty(property)}
              >
                <div className="property-item-header">
                  <span className="content-type-badge">{contentTypeLabel}</span>
                </div>
                <div className="property-item-title">{displayTitle}</div>
                <div className="property-item-url">{urlDomain}</div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};
