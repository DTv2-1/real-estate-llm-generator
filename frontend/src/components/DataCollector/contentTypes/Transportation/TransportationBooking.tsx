import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Booking information interface
 */
interface BookingInfo {
  required?: boolean;
  advance_booking?: string;
  cancellation_policy?: string;
  payment_methods?: string[];
  booking_url?: string;
}

/**
 * Props for TransportationBooking component
 */
interface TransportationBookingProps {
  /** Booking information */
  bookingInfo: BookingInfo;
}

/**
 * Component for displaying booking information
 * Shows booking requirements, policies, and payment methods
 * 
 * @component
 */
export const TransportationBooking: React.FC<TransportationBookingProps> = ({
  bookingInfo
}) => {
  return (
    <SectionCard title="Información de Reserva" icon="📝">
      <FieldRenderer
        label="Reserva Requerida"
        value={bookingInfo.required}
        type="boolean"
        icon="✅"
      />
      <FieldRenderer
        label="Reserva Anticipada"
        value={bookingInfo.advance_booking}
        icon="⏰"
      />
      <FieldRenderer
        label="Política de Cancelación"
        value={bookingInfo.cancellation_policy}
        icon="❌"
      />
      
      {bookingInfo.payment_methods && bookingInfo.payment_methods.length > 0 && (
        <FieldRenderer
          label="Métodos de Pago"
          value=""
          type="list"
          listItems={bookingInfo.payment_methods}
          icon="💳"
        />
      )}
      
      <FieldRenderer
        label="URL de Reserva"
        value={bookingInfo.booking_url}
        type="url"
        icon="🔗"
      />
    </SectionCard>
  );
};
