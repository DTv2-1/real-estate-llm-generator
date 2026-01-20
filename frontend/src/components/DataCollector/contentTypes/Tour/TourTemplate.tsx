import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { TourSchedule } from './TourSchedule';
import { TourPricing } from './TourPricing';
import { TourInclusions } from './TourInclusions';

/**
 * Props for TourTemplate component
 */
interface TourTemplateProps {
  /** Property data for tour/activity */
  property: PropertyData;
}

/**
 * Template component for displaying tour and activity information
 * Organizes tour details including schedules, pricing, and inclusions
 * 
 * @component
 * @example
 * ```tsx
 * <TourTemplate property={tourData} />
 * ```
 */
export const TourTemplate: React.FC<TourTemplateProps> = ({ property }) => {
  return (
    <div className="tour-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información del Tour" icon="🎯">
        <FieldRenderer label="Título" value={property.title} icon="🎪" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
      </SectionCard>

      {/* Description */}
      {property.description && (
        <SectionCard title="Descripción del Tour" icon="📄">
          <div className="description-text">{property.description}</div>
        </SectionCard>
      )}

      {/* Pricing */}
      {property.price_details && (
        <TourPricing priceDetails={property.price_details} />
      )}

      {/* Schedule */}
      {property.tour_schedule && (
        <TourSchedule schedule={property.tour_schedule} />
      )}

      {/* Location */}
      {property.location && typeof property.location === 'object' && (
        <SectionCard title="Punto de Encuentro" icon="📍">
          <FieldRenderer
            label="Dirección"
            value={property.location.address}
            icon="🏢"
          />
          <FieldRenderer label="Ciudad" value={property.location.city} icon="🌆" />
          <FieldRenderer label="País" value={property.location.country} icon="🌍" />
          {property.location.coordinates && (
            <FieldRenderer
              label="Coordenadas"
              value={`${property.location.coordinates.lat}, ${property.location.coordinates.lng}`}
              icon="🗺️"
            />
          )}
        </SectionCard>
      )}

      {/* Inclusions/Exclusions */}
      {(property.inclusions || property.exclusions) && (
        <TourInclusions
          inclusions={property.inclusions}
          exclusions={property.exclusions}
        />
      )}

      {/* Requirements */}
      {property.requirements && property.requirements.length > 0 && (
        <SectionCard title="Requisitos" icon="⚠️">
          <FieldRenderer
            label="Requisitos"
            value=""
            type="list"
            listItems={property.requirements}
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
