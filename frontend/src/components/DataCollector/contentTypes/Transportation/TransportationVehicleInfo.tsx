import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Vehicle information interface
 */
interface VehicleInfo {
  type?: string;
  capacity?: number;
  features?: string[];
  accessibility?: boolean;
  air_conditioning?: boolean;
  wifi?: boolean;
}

/**
 * Props for TransportationVehicleInfo component
 */
interface TransportationVehicleInfoProps {
  /** Vehicle information */
  vehicleInfo: VehicleInfo;
}

/**
 * Component for displaying vehicle information
 * Shows vehicle type, capacity, and available features
 * 
 * @component
 */
export const TransportationVehicleInfo: React.FC<TransportationVehicleInfoProps> = ({
  vehicleInfo
}) => {
  return (
    <SectionCard title="Información del Vehículo" icon="🚐">
      <FieldRenderer
        label="Tipo de Vehículo"
        value={vehicleInfo.type}
        icon="🚙"
      />
      <FieldRenderer
        label="Capacidad"
        value={vehicleInfo.capacity ? `${vehicleInfo.capacity} pasajeros` : null}
        type="number"
        icon="👥"
      />
      <FieldRenderer
        label="Accesibilidad"
        value={vehicleInfo.accessibility}
        type="boolean"
        icon="♿"
      />
      <FieldRenderer
        label="Aire Acondicionado"
        value={vehicleInfo.air_conditioning}
        type="boolean"
        icon="❄️"
      />
      <FieldRenderer
        label="WiFi"
        value={vehicleInfo.wifi}
        type="boolean"
        icon="📶"
      />
      
      {vehicleInfo.features && vehicleInfo.features.length > 0 && (
        <FieldRenderer
          label="Características Adicionales"
          value=""
          type="list"
          listItems={vehicleInfo.features}
          icon="⭐"
        />
      )}
    </SectionCard>
  );
};
