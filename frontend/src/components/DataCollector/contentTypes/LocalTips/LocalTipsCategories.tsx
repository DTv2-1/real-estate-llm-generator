import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Tips organized by category interface
 */
interface TipsByCategory {
  [category: string]: string[];
}

/**
 * Props for LocalTipsCategories component
 */
interface LocalTipsCategoriesProps {
  /** Tips organized by category */
  tipsByCategory: TipsByCategory;
}

/**
 * Component for displaying local tips organized by categories
 * Groups tips into collapsible sections by category type
 * 
 * @component
 */
export const LocalTipsCategories: React.FC<LocalTipsCategoriesProps> = ({
  tipsByCategory
}) => {
  // Map category keys to friendly names and icons
  const categoryConfig: Record<string, { name: string; icon: string }> = {
    dining: { name: 'Gastronomía', icon: '🍽️' },
    accommodation: { name: 'Alojamiento', icon: '🏨' },
    transportation: { name: 'Transporte', icon: '🚗' },
    safety: { name: 'Seguridad', icon: '🛡️' },
    culture: { name: 'Cultura', icon: '🎭' },
    shopping: { name: 'Compras', icon: '🛍️' },
    nightlife: { name: 'Vida Nocturna', icon: '🌙' },
    outdoor: { name: 'Actividades al Aire Libre', icon: '🏞️' },
    health: { name: 'Salud', icon: '⚕️' },
    communication: { name: 'Comunicación', icon: '📱' },
    money: { name: 'Dinero', icon: '💵' },
    weather: { name: 'Clima', icon: '🌤️' }
  };

  return (
    <div className="local-tips-categories">
      {Object.entries(tipsByCategory).map(([category, tips]) => {
        const config = categoryConfig[category] || {
          name: category.charAt(0).toUpperCase() + category.slice(1),
          icon: '💡'
        };

        return (
          <SectionCard
            key={category}
            title={config.name}
            icon={config.icon}
            collapsible={true}
            defaultCollapsed={false}
          >
            <FieldRenderer
              label=""
              value=""
              type="list"
              listItems={tips}
            />
          </SectionCard>
        );
      })}
    </div>
  );
};
