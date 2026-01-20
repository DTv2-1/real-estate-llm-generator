import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { TransportationSchedule } from './TransportationSchedule';
import { TransportationRoutes } from './TransportationRoutes';
import { TransportationPricing } from './TransportationPricing';
import { TransportationVehicleInfo } from './TransportationVehicleInfo';
import { TransportationBooking } from './TransportationBooking';

/**
 * Props for TransportationTemplate component
 */
interface TransportationTemplateProps {
  /** Property data for transportation service */
  property: PropertyData;
}

/**
 * Template component for displaying transportation service information
 * Organizes transport details including routes, schedules, pricing, and booking
 * 
 * @component
 * @example
 * ```tsx
 * <TransportationTemplate property={transportData} />
 * ```
 */
export const TransportationTemplate: React.FC<TransportationTemplateProps> = ({
  property
}) => {
  return (
    <div className="transportation-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información del Servicio" icon="🚗">
        <FieldRenderer label="Nombre del Servicio" value={property.title} icon="🚕" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer
          label="Tipo de Transporte"
          value={property.transport_type}
          icon="🚌"
        />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
      </SectionCard>

      {/* Description */}
      {property.description && (
        <SectionCard title="Descripción del Servicio" icon="📄">
          <div className="description-text">{property.description}</div>
        </SectionCard>
      )}

      {/* Vehicle Information */}
      {property.vehicle_info && (
        <TransportationVehicleInfo vehicleInfo={property.vehicle_info} />
      )}

      {/* Routes */}
      {property.routes && property.routes.length > 0 && (
        <TransportationRoutes routes={property.routes} />
      )}

      {/* Schedule */}
      {property.schedule && (
        <TransportationSchedule schedule={property.schedule} />
      )}

      {/* Pricing */}
      {property.price_details && (
        <TransportationPricing priceDetails={property.price_details} />
      )}

      {/* Booking Information */}
      {property.booking_info && (
        <TransportationBooking bookingInfo={property.booking_info} />
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
