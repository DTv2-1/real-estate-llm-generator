import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Tour schedule interface
 */
interface TourScheduleData {
  days_available?: string[];
  start_times?: string[];
  duration?: string;
  frequency?: string;
}

/**
 * Props for TourSchedule component
 */
interface TourScheduleProps {
  /** Tour schedule information */
  schedule: TourScheduleData;
}

/**
 * Component for displaying tour schedule and timing information
 * Shows available days, start times, duration, and frequency
 * 
 * @component
 */
export const TourSchedule: React.FC<TourScheduleProps> = ({ schedule }) => {
  return (
    <SectionCard title="Horarios y Disponibilidad" icon="📅">
      <FieldRenderer
        label="Días Disponibles"
        value=""
        type="list"
        listItems={schedule.days_available}
        icon="📆"
      />
      <FieldRenderer
        label="Horarios de Inicio"
        value=""
        type="list"
        listItems={schedule.start_times}
        icon="🕐"
      />
      <FieldRenderer label="Duración" value={schedule.duration} icon="⏱️" />
      <FieldRenderer label="Frecuencia" value={schedule.frequency} icon="🔄" />
    </SectionCard>
  );
};
