import React from 'react';
import type { PropertyData } from '../../types';

/**
 * Props for TransportationTemplate component
 */
interface TransportationTemplateProps {
  /** Property data for transportation service */
  property: PropertyData;
}

// Transport type icons mapping
const TRANSPORT_ICONS: Record<string, string> = {
  bus: '🚌',
  shuttle: '🚐',
  car: '🚗',
  taxi: '🚕',
  flight: '✈️',
  ferry: '⛴️',
  train: '🚆',
  bike: '🚴',
  walk: '🚶',
};

// Get icon for transport type
const getTransportIcon = (type: string): string => {
  return TRANSPORT_ICONS[type?.toLowerCase()] || '🚗';
};

/**
 * Template component for displaying transportation route comparison
 * Shows all available transportation options with pricing, duration, and recommendations
 */
export const TransportationTemplate: React.FC<TransportationTemplateProps> = ({
  property
}) => {
  const routeOptions = property.route_options || [];
  const hasMultipleOptions = routeOptions.length > 0;

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-5xl">🗺️</span>
              <div>
                <h1 className="text-3xl font-bold">
                  {property.route_name || property.title || 'Opciones de Transporte'}
                </h1>
                {property.departure_location && property.arrival_location && (
                  <p className="text-blue-100 text-lg mt-2">
                    📍 {property.departure_location} → {property.arrival_location}
                  </p>
                )}
              </div>
            </div>
            
            {property.distance_km && (
              <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
                <span className="text-2xl">📏</span>
                <span className="text-lg font-semibold">{property.distance_km} km</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Recommendations */}
      {(property.fastest_option || property.cheapest_option || property.recommended_option) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Fastest Option */}
          {property.fastest_option && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-5 hover:shadow-lg transition-all">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">⚡</span>
                <h3 className="text-lg font-bold text-green-800">Más Rápido</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getTransportIcon(property.fastest_option.transport_type)}</span>
                  <span className="font-semibold text-gray-700 capitalize">
                    {property.fastest_option.transport_type}
                  </span>
                </div>
                <div className="text-2xl font-bold text-green-700">
                  {property.fastest_option.duration_hours}h
                </div>
                {property.fastest_option.price_usd && (
                  <div className="text-gray-600">
                    ${property.fastest_option.price_usd} USD
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Cheapest Option */}
          {property.cheapest_option && (
            <div className="bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-200 rounded-xl p-5 hover:shadow-lg transition-all">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">💰</span>
                <h3 className="text-lg font-bold text-yellow-800">Más Económico</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getTransportIcon(property.cheapest_option.transport_type)}</span>
                  <span className="font-semibold text-gray-700 capitalize">
                    {property.cheapest_option.transport_type}
                  </span>
                </div>
                <div className="text-2xl font-bold text-yellow-700">
                  ${property.cheapest_option.price_usd} USD
                </div>
                {property.cheapest_option.duration_hours && (
                  <div className="text-gray-600">
                    {property.cheapest_option.duration_hours}h
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Recommended Option */}
          {property.recommended_option && (
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-xl p-5 hover:shadow-lg transition-all">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">⭐</span>
                <h3 className="text-lg font-bold text-purple-800">Recomendado</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getTransportIcon(property.recommended_option.transport_type)}</span>
                  <span className="font-semibold text-gray-700 capitalize">
                    {property.recommended_option.transport_type}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  {property.recommended_option.duration_hours && (
                    <span className="font-semibold text-gray-700">
                      {property.recommended_option.duration_hours}h
                    </span>
                  )}
                  {property.recommended_option.price_usd && (
                    <span className="font-semibold text-gray-700">
                      ${property.recommended_option.price_usd}
                    </span>
                  )}
                </div>
                {property.recommended_option.reason && (
                  <p className="text-sm text-gray-600 italic">
                    {property.recommended_option.reason}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* All Transportation Options */}
      {hasMultipleOptions && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <span className="text-3xl">🚦</span>
            Todas las Opciones ({routeOptions.length})
          </h2>
          
          <div className="space-y-4">
            {routeOptions.map((option: any, index: number) => (
              <div
                key={index}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  {/* Left: Transport Info */}
                  <div className="flex items-start gap-4 flex-1">
                    <span className="text-4xl">{getTransportIcon(option.transport_type)}</span>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-800 capitalize mb-2">
                        {option.transport_type}
                        {option.operator && (
                          <span className="text-base font-normal text-gray-600 ml-2">
                            ({option.operator})
                          </span>
                        )}
                      </h3>
                      
                      {option.route_description && (
                        <p className="text-gray-600 mb-3">{option.route_description}</p>
                      )}

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                        {/* Duration */}
                        {option.duration_hours && (
                          <div className="flex items-center gap-2">
                            <span className="text-xl">⏱️</span>
                            <div>
                              <div className="text-xs text-gray-500">Duración</div>
                              <div className="font-semibold text-gray-800">
                                {option.duration_hours}h
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Price */}
                        {(option.price_min_usd || option.price_max_usd || option.price_usd) && (
                          <div className="flex items-center gap-2">
                            <span className="text-xl">💵</span>
                            <div>
                              <div className="text-xs text-gray-500">Precio</div>
                              <div className="font-semibold text-gray-800">
                                {option.price_usd 
                                  ? `$${option.price_usd}`
                                  : `$${option.price_min_usd}-${option.price_max_usd}`
                                } USD
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Frequency */}
                        {option.frequency && (
                          <div className="flex items-center gap-2">
                            <span className="text-xl">🔄</span>
                            <div>
                              <div className="text-xs text-gray-500">Frecuencia</div>
                              <div className="font-semibold text-gray-800 capitalize">
                                {option.frequency}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Booking */}
                        {option.booking_required !== undefined && (
                          <div className="flex items-center gap-2">
                            <span className="text-xl">
                              {option.booking_required ? '📅' : '🎫'}
                            </span>
                            <div>
                              <div className="text-xs text-gray-500">Reserva</div>
                              <div className="font-semibold text-gray-800">
                                {option.booking_required ? 'Requerida' : 'No requerida'}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Departure/Arrival Points */}
                      {(option.departure_point || option.arrival_point) && (
                        <div className="mt-4 flex items-center gap-3 text-sm text-gray-600">
                          {option.departure_point && (
                            <span>📍 Salida: {option.departure_point}</span>
                          )}
                          {option.arrival_point && (
                            <span>🎯 Llegada: {option.arrival_point}</span>
                          )}
                        </div>
                      )}

                      {/* Amenities */}
                      {option.amenities && option.amenities.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {option.amenities.map((amenity: string, i: number) => (
                            <span
                              key={i}
                              className="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full"
                            >
                              ✓ {amenity}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Travel Tips */}
      {property.travel_tips && property.travel_tips.length > 0 && (
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl p-6 border-2 border-orange-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            Consejos de Viaje
          </h2>
          <ul className="space-y-2">
            {property.travel_tips.map((tip: string, index: number) => (
              <li key={index} className="flex items-start gap-3">
                <span className="text-orange-500 mt-1">▸</span>
                <span className="text-gray-700">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Things to Know */}
      {property.things_to_know && property.things_to_know.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl p-6 border-2 border-blue-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-2xl">ℹ️</span>
            Información Importante
          </h2>
          <ul className="space-y-2">
            {property.things_to_know.map((info: string, index: number) => (
              <li key={index} className="flex items-start gap-3">
                <span className="text-blue-500 mt-1">•</span>
                <span className="text-gray-700">{info}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Best Time to Travel */}
      {property.best_time_to_travel && (
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl p-6 border-2 border-green-200">
          <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
            <span className="text-2xl">🕐</span>
            Mejor Hora para Viajar
          </h2>
          <p className="text-gray-700 text-lg">{property.best_time_to_travel}</p>
        </div>
      )}

      {/* Web Search Context (Collapsible) */}
      {property.web_search_context && (
        <details className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <summary className="cursor-pointer font-semibold text-gray-700 flex items-center gap-2">
            <span className="text-xl">📚</span>
            Información Adicional (de web search)
          </summary>
          <div className="mt-4 text-gray-600 whitespace-pre-wrap text-sm leading-relaxed">
            {property.web_search_context}
          </div>
        </details>
      )}
    </div>
  );
};
