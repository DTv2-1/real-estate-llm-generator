import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { RestaurantMenu } from './RestaurantMenu';

/**
 * Props for RestaurantTemplate component
 */
interface RestaurantTemplateProps {
  /** Property data for restaurant */
  property: PropertyData;
}

/**
 * Template component for displaying restaurant information
 * Organizes restaurant details including menu, hours, and amenities
 * 
 * @component
 * @example
 * ```tsx
 * <RestaurantTemplate property={restaurantData} />
 * ```
 */
export const RestaurantTemplate: React.FC<RestaurantTemplateProps> = ({ property }) => {
  return (
    <div className="restaurant-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información del Restaurante" icon="🍽️">
        <FieldRenderer label="Nombre" value={property.title} icon="🏪" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer label="Tipo de Cocina" value={property.cuisine_type} icon="👨‍🍳" />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
      </SectionCard>

      {/* Description */}
      {property.description && (
        <SectionCard title="Descripción" icon="📄">
          <div className="description-text">{property.description}</div>
        </SectionCard>
      )}

      {/* Price Range */}
      {property.price_details && (
        <SectionCard title="Rango de Precios" icon="💰">
          <FieldRenderer
            label="Rango de Precios"
            value={property.price_details.display_price}
            icon="💵"
          />
          <FieldRenderer
            label="Precio Promedio"
            value={property.price_details.average_price}
            type="currency"
            icon="💳"
          />
          <FieldRenderer label="Moneda" value={property.price_details.currency} icon="💱" />
        </SectionCard>
      )}

      {/* Operating Hours */}
      {property.operating_hours && (
        <SectionCard title="Horarios de Atención" icon="🕐">
          <div className="operating-hours">
            {Object.entries(property.operating_hours).map(([day, hours]) => (
              <FieldRenderer
                key={day}
                label={day.charAt(0).toUpperCase() + day.slice(1)}
                value={hours as string}
                icon="📅"
              />
            ))}
          </div>
        </SectionCard>
      )}

      {/* Menu */}
      {property.menu_items && property.menu_items.length > 0 && (
        <RestaurantMenu menuItems={property.menu_items} />
      )}

      {/* Location */}
      {property.location && typeof property.location === 'object' && (
        <SectionCard title="Ubicación" icon="📍">
          <FieldRenderer
            label="Dirección"
            value={property.location.address}
            icon="🏢"
          />
          <FieldRenderer label="Ciudad" value={property.location.city} icon="🌆" />
          <FieldRenderer label="Estado" value={property.location.state} icon="🗺️" />
          <FieldRenderer label="País" value={property.location.country} icon="🌍" />
        </SectionCard>
      )}

      {/* Features & Amenities */}
      {property.features && property.features.length > 0 && (
        <SectionCard title="Características y Amenidades" icon="⭐">
          <FieldRenderer
            label="Amenidades"
            value=""
            type="list"
            listItems={property.features}
          />
        </SectionCard>
      )}

      {/* Images */}
      {property.images && property.images.length > 0 && (
        <SectionCard title={`Galería (${property.images.length})`} icon="📷">
          <div className="images-grid">
            {property.images.map((imageUrl: string, index: number) => (
              <div key={index} className="image-thumbnail">
                <img src={imageUrl} alt={`Imagen ${index + 1}`} loading="lazy" />
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Contact Information */}
      {property.contact && (
        <SectionCard title="Información de Contacto" icon="📞">
          <FieldRenderer label="Nombre" value={property.contact.name} icon="👤" />
          <FieldRenderer
            label="Email"
            value={property.contact.email}
            type="email"
            icon="📧"
          />
          <FieldRenderer
            label="Teléfono"
            value={property.contact.phone}
            type="tel"
            icon="☎️"
          />
          <FieldRenderer
            label="WhatsApp"
            value={property.contact.whatsapp}
            type="tel"
            icon="💬"
          />
        </SectionCard>
      )}
    </div>
  );
};
