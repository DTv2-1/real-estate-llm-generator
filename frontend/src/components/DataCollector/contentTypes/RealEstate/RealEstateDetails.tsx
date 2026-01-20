import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Property details interface
 */
interface PropertyDetails {
  property_type?: string;
  bedrooms?: number;
  bathrooms?: number;
  area?: number;
  area_unit?: string;
  lot_size?: number;
  lot_size_unit?: string;
  year_built?: number;
  furnished?: boolean;
  parking_spaces?: number;
  floors?: number;
  hoa_fee?: number;
}

/**
 * Props for RealEstateDetails component
 */
interface RealEstateDetailsProps {
  /** Property details data */
  details: PropertyDetails;
}

/**
 * Component for displaying real estate property details
 * Shows property specifications like bedrooms, bathrooms, area, etc.
 * 
 * @component
 */
export const RealEstateDetails: React.FC<RealEstateDetailsProps> = ({ details }) => {
  const formatArea = (area: number, unit?: string) => {
    return `${area.toLocaleString()} ${unit || 'm²'}`;
  };

  return (
    <SectionCard title="Detalles de la Propiedad" icon="🏠">
      <FieldRenderer
        label="Tipo de Propiedad"
        value={details.property_type}
        icon="🏘️"
      />

      <div className="details-grid">
        <FieldRenderer
          label="Habitaciones"
          value={details.bedrooms}
          type="number"
          icon="🛏️"
        />
        <FieldRenderer
          label="Baños"
          value={details.bathrooms}
          type="number"
          icon="🚿"
        />
        {details.area && (
          <FieldRenderer
            label="Área"
            value={formatArea(details.area, details.area_unit)}
            icon="📐"
          />
        )}
        {details.lot_size && (
          <FieldRenderer
            label="Tamaño del Lote"
            value={formatArea(details.lot_size, details.lot_size_unit)}
            icon="🌳"
          />
        )}
        <FieldRenderer
          label="Año de Construcción"
          value={details.year_built}
          type="number"
          icon="📅"
        />
        <FieldRenderer
          label="Amueblado"
          value={details.furnished}
          type="boolean"
          icon="🛋️"
        />
        <FieldRenderer
          label="Estacionamientos"
          value={details.parking_spaces}
          type="number"
          icon="🚗"
        />
        <FieldRenderer
          label="Pisos"
          value={details.floors}
          type="number"
          icon="🏢"
        />
        {details.hoa_fee && (
          <FieldRenderer
            label="Cuota de HOA"
            value={`$${details.hoa_fee.toLocaleString()}`}
            type="currency"
            icon="💳"
          />
        )}
      </div>
    </SectionCard>
  );
};
