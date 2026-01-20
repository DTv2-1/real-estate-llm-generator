import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Schedule information interface
 */
interface Schedule {
  operating_days?: string[];
  first_departure?: string;
  last_departure?: string;
  frequency?: string;
  departure_times?: string[];
}

/**
 * Props for TransportationSchedule component
 */
interface TransportationScheduleProps {
  /** Schedule information */
  schedule: Schedule;
}

/**
 * Component for displaying transportation schedule
 * Shows operating days, departure times, and frequency
 * 
 * @component
 */
export const TransportationSchedule: React.FC<TransportationScheduleProps> = ({
  schedule
}) => {
  return (
    <SectionCard title="Horarios y Frecuencia" icon="📅">
      <FieldRenderer
        label="Días de Operación"
        value=""
        type="list"
        listItems={schedule.operating_days}
        icon="📆"
      />
      <FieldRenderer
        label="Primera Salida"
        value={schedule.first_departure}
        icon="🌅"
      />
      <FieldRenderer
        label="Última Salida"
        value={schedule.last_departure}
        icon="🌇"
      />
      <FieldRenderer
        label="Frecuencia"
        value={schedule.frequency}
        icon="🔄"
      />
      {schedule.departure_times && schedule.departure_times.length > 0 && (
        <FieldRenderer
          label="Horarios de Salida"
          value=""
          type="list"
          listItems={schedule.departure_times}
          icon="🕐"
        />
      )}
    </SectionCard>
  );
};
