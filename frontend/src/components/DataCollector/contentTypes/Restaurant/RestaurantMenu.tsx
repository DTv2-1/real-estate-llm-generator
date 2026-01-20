import React from 'react';
import { SectionCard } from '../shared/SectionCard';

/**
 * Menu item interface
 */
interface MenuItem {
  name: string;
  description?: string;
  price?: string | number;
  category?: string;
}

/**
 * Props for RestaurantMenu component
 */
interface RestaurantMenuProps {
  /** Array of menu items */
  menuItems: MenuItem[];
}

/**
 * Component for displaying restaurant menu
 * Organizes menu items by category with prices and descriptions
 * 
 * @component
 */
export const RestaurantMenu: React.FC<RestaurantMenuProps> = ({ menuItems }) => {
  // Group menu items by category
  const groupedItems = menuItems.reduce((acc, item) => {
    const category = item.category || 'General';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as Record<string, MenuItem[]>);

  return (
    <SectionCard title="Menú" icon="📋">
      <div className="restaurant-menu">
        {Object.entries(groupedItems).map(([category, items]) => (
          <div key={category} className="menu-category">
            <h4 className="menu-category-title">{category}</h4>
            <div className="menu-items">
              {items.map((item, index) => (
                <div key={index} className="menu-item">
                  <div className="menu-item-header">
                    <span className="menu-item-name">{item.name}</span>
                    {item.price && (
                      <span className="menu-item-price">
                        {typeof item.price === 'number'
                          ? `$${item.price.toFixed(2)}`
                          : item.price}
                      </span>
                    )}
                  </div>
                  {item.description && (
                    <p className="menu-item-description">{item.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
};
