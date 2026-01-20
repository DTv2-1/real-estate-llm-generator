import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { RealEstateDetails } from './RealEstateDetails';

/**
 * Props for RealEstateTemplate component
 */
interface RealEstateTemplateProps {
  /** Property data for real estate */
  property: PropertyData;
}

/**
 * Template component for displaying real estate property data
 * Organizes property information in a structured, user-friendly layout
 * 
 * @component
 * @example
 * ```tsx
 * <RealEstateTemplate property={propertyData} />
 * ```
 */
export const RealEstateTemplate: React.FC<RealEstateTemplateProps> = ({ property }) => {
  return (
    <div className="real-estate-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información Básica" icon="📋">
        <FieldRenderer label="Título" value={property.title} icon="🏠" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
      </SectionCard>

      {/* Price Details */}
      {property.price_details && (
        <SectionCard title="Detalles de Precio" icon="💰">
          <FieldRenderer
            label="Precio de Venta"
            value={property.price_details.display_price || property.price_details.sale_price}
            type="currency"
            icon="💵"
          />
          <FieldRenderer
            label="Precio de Renta"
            value={property.price_details.rental_price}
            type="currency"
            icon="🏠"
          />
          <FieldRenderer
            label="Moneda"
            value={property.price_details.currency}
            icon="💱"
          />
        </SectionCard>
      )}

      {/* Property Details */}
      {property.details && (
        <RealEstateDetails details={property.details} />
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
          <FieldRenderer
            label="Estado/Provincia"
            value={property.location.state}
            icon="🗺️"
          />
          <FieldRenderer label="País" value={property.location.country} icon="🌍" />
          <FieldRenderer
            label="Código Postal"
            value={property.location.postal_code}
            icon="📮"
          />
        </SectionCard>
      )}

      {/* Description */}
      {property.description && (
        <SectionCard title="Descripción" icon="📄">
          <div className="description-text">{property.description}</div>
        </SectionCard>
      )}

      {/* Features */}
      {property.features && property.features.length > 0 && (
        <SectionCard title="Características y Amenidades" icon="⭐">
          <FieldRenderer
            label="Características"
            value=""
            type="list"
            listItems={property.features}
          />
        </SectionCard>
      )}

      {/* Images */}
      {property.images && property.images.length > 0 && (
        <SectionCard title={`Galería de Imágenes (${property.images.length})`} icon="📷">
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
