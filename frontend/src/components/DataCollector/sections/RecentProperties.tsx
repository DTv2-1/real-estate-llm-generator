import React from 'react';
import './RecentProperties.css';
import type { PropertyData } from '../types';
import { formatTimeAgo, formatPrice } from '../utils/formatters';

/**
 * Props for RecentProperties component
 */
interface RecentPropertiesProps {
  /** Array of recent properties to display */
  properties: PropertyData[];
  /** Handler when a property card is clicked */
  onSelectProperty: (property: PropertyData) => void;
  /** Currently selected property ID */
  selectedPropertyId?: string;
  /** Maximum number of properties to display */
  maxItems?: number;
}

/**
 * Grid display of recent properties with preview cards
 * Shows thumbnail, title, price, and timestamp for each property
 * 
 * @component
 * @example
 * ```tsx
 * <RecentProperties
 *   properties={recentProps}
 *   onSelectProperty={handleSelect}
 *   selectedPropertyId="123"
 *   maxItems={6}
 * />
 * ```
 */
export const RecentProperties: React.FC<RecentPropertiesProps> = ({
  properties,
  onSelectProperty,
  selectedPropertyId,
  maxItems = 6
}) => {
  const displayProperties = properties.slice(0, maxItems);

  if (displayProperties.length === 0) {
    return null;
  }

  return (
    <section className="recent-properties">
      <h3 className="recent-properties-title">
        <span className="title-icon">🕒</span>
        Propiedades Recientes
      </h3>
      <div className="properties-grid">
        {displayProperties.map((property, index) => (
          <PropertyCard
            key={property.id || index}
            property={property}
            isSelected={property.id === selectedPropertyId}
            onClick={() => onSelectProperty(property)}
          />
        ))}
      </div>
    </section>
  );
};

/**
 * Props for PropertyCard component
 */
interface PropertyCardProps {
  /** Property data to display */
  property: PropertyData;
  /** Whether this card is currently selected */
  isSelected: boolean;
  /** Handler when card is clicked */
  onClick: () => void;
}

/**
 * Individual property card with thumbnail and key details
 * Displays image, title, price, location, and timestamp
 * 
 * @component
 */
export const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  isSelected,
  onClick
}) => {
  const getImageUrl = () => {
    if (property.images && property.images.length > 0) {
      return property.images[0];
    }
    return '/placeholder-property.jpg';
  };

  const getBadgeInfo = () => {
    const contentType = property.content_type || property.detected_content_type || 'real-estate';
    const pageType = property.page_type || '';
    
    const badges: Record<string, { icon: string; label: string; color: string }> = {
      'local_tips': { icon: '🗺️', label: 'Local Tips', color: 'bg-blue-500' },
      'restaurant': { icon: '🍽️', label: 'Restaurante', color: 'bg-orange-500' },
      'tour': { icon: '🎯', label: 'Tour', color: 'bg-green-500' },
      'transportation': { icon: '🚌', label: 'Transporte', color: 'bg-purple-500' },
      'real-estate': { icon: '🏠', label: 'Propiedad', color: 'bg-indigo-500' },
    };
    
    const badge = badges[contentType] || badges['real-estate'];
    const pageLabel = pageType === 'general' ? '📋 General' : pageType === 'specific' ? '📍 Específico' : '';
    
    return { ...badge, pageLabel };
  };

  const getPrice = () => {
    // For non-real-estate content, show different info
    const contentType = property.content_type || property.detected_content_type || 'real-estate';
    
    if (contentType === 'local_tips') {
      const destCount = property.destinations_covered?.length;
      return destCount ? `${destCount} destinos` : 'Guía de viaje';
    }
    
    if (contentType === 'restaurant') {
      if (property.price_range) {
        return property.price_range;
      }
      if (property.cuisine) {
        return property.cuisine;
      }
      return 'Restaurante';
    }
    
    if (contentType === 'tour') {
      if (property.duration) {
        return `Duración: ${property.duration}`;
      }
      return 'Tour / Actividad';
    }
    
    if (contentType === 'transportation') {
      if (property.route) {
        return property.route;
      }
      if (property.transport_type) {
        return property.transport_type;
      }
      return 'Transporte';
    }
    
    // Real estate pricing
    if (property.price_details?.display_price) {
      return property.price_details.display_price;
    }
    if (property.price_details?.sale_price) {
      return formatPrice(property.price_details.sale_price);
    }
    if (property.price_details?.rental_price) {
      return formatPrice(property.price_details.rental_price);
    }
    return 'Precio no disponible';
  };

  const getLocation = () => {
    const parts = [];
    
    // Type guard for location object
    if (typeof property.location === 'object' && property.location) {
      if (property.location.city) parts.push(property.location.city);
      if (property.location.state) parts.push(property.location.state);
      return parts.join(', ') || 'Ubicación no especificada';
    }
    
    // Handle string location
    if (typeof property.location === 'string') {
      return property.location;
    }
    
    return 'Ubicación no especificada';
  };

  const badgeInfo = getBadgeInfo();

  return (
    <article
      className={`property-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyPress={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          onClick();
        }
      }}
    >
      <div className="card-image-container">
        <img
          src={getImageUrl()}
          alt={property.title || 'Propiedad'}
          className="card-image"
          loading="lazy"
        />
        <span className={`card-badge ${badgeInfo.color}`}>
          <span className="badge-icon">{badgeInfo.icon}</span>
          <span className="badge-label">{badgeInfo.label}</span>
        </span>
        {badgeInfo.pageLabel && (
          <span className="card-badge-secondary">
            {badgeInfo.pageLabel}
          </span>
        )}
      </div>

      <div className="card-content">
        <h4 className="card-title" title={property.title}>
          {property.title || 'Sin título'}
        </h4>

        <div className="card-price">{getPrice()}</div>

        <div className="card-location">
          <span className="location-icon">📍</span>
          {getLocation()}
        </div>

        {property.timestamp && (
          <div className="card-timestamp">
            {formatTimeAgo(property.timestamp)}
          </div>
        )}
      </div>
    </article>
  );
};
