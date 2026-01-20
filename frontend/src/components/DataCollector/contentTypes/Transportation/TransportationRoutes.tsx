import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Route information interface
 */
interface Route {
  origin: string;
  destination: string;
  distance?: string;
  duration?: string;
  stops?: string[];
}

/**
 * Props for TransportationRoutes component
 */
interface TransportationRoutesProps {
  /** Array of available routes */
  routes: Route[];
}

/**
 * Component for displaying transportation routes
 * Shows origin, destination, distance, duration, and stops
 * 
 * @component
 */
export const TransportationRoutes: React.FC<TransportationRoutesProps> = ({ routes }) => {
  return (
    <SectionCard title="Rutas Disponibles" icon="🗺️">
      <div className="transportation-routes">
        {routes.map((route, index) => (
          <div key={index} className="route-item">
            <h4 className="route-title">
              {route.origin} → {route.destination}
            </h4>
            <div className="route-details">
              <FieldRenderer
                label="Distancia"
                value={route.distance}
                icon="📏"
              />
              <FieldRenderer
                label="Duración"
                value={route.duration}
                icon="⏱️"
              />
              {route.stops && route.stops.length > 0 && (
                <FieldRenderer
                  label="Paradas"
                  value=""
                  type="list"
                  listItems={route.stops}
                  icon="🚏"
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
};
