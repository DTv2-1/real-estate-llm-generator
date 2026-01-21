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
 * Clean markdown formatting from text
 */
const cleanMarkdown = (text: string): string => {
  if (!text) return text;
  
  let cleaned = text;
  
  // Decode HTML entities
  cleaned = cleaned
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
  
  // Remove markdown links [text](url) -> text
  cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
  
  // Remove bold/italic markers
  cleaned = cleaned
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/__/g, '')
    .replace(/_/g, '');
  
  // Remove headers
  cleaned = cleaned.replace(/^#{1,6}\s+/gm, '');
  
  // Replace markdown bullets with simple bullets
  cleaned = cleaned.replace(/^\s*[-*+]\s+/gm, '• ');
  
  // Remove common emojis
  cleaned = cleaned.replace(/[✅❌💰🎯📍⭐🌍🎪🔗🎭🗺️🏷️⏱️💪📄🌐💵📅🕐🎒🏢🌆]/g, '');
  
  // Remove horizontal rules
  cleaned = cleaned.replace(/^---+$/gm, '');
  
  // Clean up extra whitespace
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
  
  return cleaned.trim();
};

/**
 * Template component for displaying tour and activity information
 * Handles both individual tours and general tour guides
 * 
 * @component
 * @example
 * ```tsx
 * <TourTemplate property={tourData} />
 * ```
 */
export const TourTemplate: React.FC<TourTemplateProps> = ({ property }) => {
  // Check if this is a general guide (multiple tours) or individual tour
  const isGeneralGuide = (property as any).page_type === 'general' || 
                         (property as any).page_type === 'general_guide';

  // Render general guide view
  if (isGeneralGuide) {
    return (
      <>
        {/* Destination Overview */}
        {(property as any).destination && (
          <SectionCard title="Destino" icon="🌍">
            <FieldRenderer 
              label="Destino" 
              value={(property as any).destination} 
              icon="📍" 
            />
            {(property as any).overview && (
              <div className="overview-text">
                <p>{(property as any).overview}</p>
              </div>
            )}
          </SectionCard>
        )}

        {/* Tour Types Available */}
        {(property as any).tour_types_available && (property as any).tour_types_available.length > 0 && (
          <SectionCard title="Tipos de Tours Disponibles" icon="🎭">
            <div className="tour-types-list">
              {(property as any).tour_types_available.map((type: string, index: number) => (
                <span key={index} className="tour-type-badge">
                  {type}
                </span>
              ))}
            </div>
          </SectionCard>
        )}

        {/* Regions */}
        {(property as any).regions && (property as any).regions.length > 0 && (
          <SectionCard title="Regiones" icon="🗺️" collapsible={true} defaultCollapsed={true}>
            {(property as any).regions.map((region: any, index: number) => (
              <div key={index} className="region-card">
                <h4 className="region-name">📍 {region.name}</h4>
                {region.description && (
                  <p className="region-description">{region.description}</p>
                )}
                {region.popular_activities && region.popular_activities.length > 0 && (
                  <div className="region-activities">
                    <strong>Actividades populares:</strong>
                    <ul>
                      {region.popular_activities.map((activity: string, idx: number) => (
                        <li key={idx}>{activity}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </SectionCard>
        )}

        {/* Featured Tours */}
        {(property as any).featured_tours && (property as any).featured_tours.length > 0 && (
          <SectionCard title="Tours Destacados" icon="⭐" collapsible={true} defaultCollapsed={true}>
            {(property as any).featured_tours.map((tour: any, index: number) => (
              <div key={index} className="featured-tour-card">
                <h4 className="tour-name">🎯 {tour.name}</h4>
                {tour.highlight && (
                  <p className="tour-highlight">{tour.highlight}</p>
                )}
                <div className="tour-meta">
                  {tour.price_usd && <span className="tour-price">${tour.price_usd} USD</span>}
                  {tour.duration && <span className="tour-duration">⏱️ {tour.duration}</span>}
                </div>
              </div>
            ))}
          </SectionCard>
        )}

        {/* Seasonal Information */}
        {(property as any).seasonal_activities && (property as any).seasonal_activities.length > 0 && (
          <SectionCard title="Actividades por Temporada" icon="🌤️" collapsible={true} defaultCollapsed={true}>
            {(property as any).seasonal_activities.map((seasonal: any, index: number) => (
              <div key={index} className="seasonal-card">
                <h4 className="season-name">📅 {seasonal.season}</h4>
                {seasonal.why_this_season && (
                  <p className="season-reason">{seasonal.why_this_season}</p>
                )}
                {seasonal.recommended_activities && seasonal.recommended_activities.length > 0 && (
                  <div className="season-activities">
                    <strong>Actividades recomendadas:</strong>
                    <ul>
                      {seasonal.recommended_activities.map((activity: string, idx: number) => (
                        <li key={idx}>{activity}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </SectionCard>
        )}

        {/* Best Season */}
        {(property as any).best_season && (
          <SectionCard title="Mejor Temporada" icon="🌞" collapsible={true} defaultCollapsed={true}>
            <FieldRenderer 
              label="Mejor época para visitar" 
              value={(property as any).best_season} 
              icon="📆" 
            />
          </SectionCard>
        )}

        {/* Tips & What to Bring */}
        {((property as any).tips || (property as any).things_to_bring || (property as any).what_to_bring) && (
          <SectionCard title="Consejos y Recomendaciones" icon="💡" collapsible={true} defaultCollapsed={true}>
            {(property as any).tips && (property as any).tips.length > 0 && (
              <div className="tips-section">
                <h4>📝 Consejos</h4>
                <ul className="tips-list">
                  {(property as any).tips.map((tip: string, index: number) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
            {((property as any).things_to_bring || (property as any).what_to_bring) && (
              <div className="bring-section">
                <h4>🎒 Qué llevar</h4>
                <div className="bring-items">
                  {((property as any).things_to_bring || (property as any).what_to_bring).map((item: string, index: number) => (
                    <span key={index} className="bring-item-badge">{item}</span>
                  ))}
                </div>
              </div>
            )}
          </SectionCard>
        )}

        {/* FAQs */}
        {(property as any).faqs && (property as any).faqs.length > 0 && (
          <SectionCard title="Preguntas Frecuentes" icon="❓" collapsible={true} defaultCollapsed={true}>
            {(property as any).faqs.map((faq: any, index: number) => (
              <div key={index} className="faq-item">
                <h4 className="faq-question">Q: {faq.question}</h4>
                <p className="faq-answer">A: {faq.answer}</p>
              </div>
            ))}
          </SectionCard>
        )}

        {/* Booking Tips */}
        {(property as any).booking_tips && (
          <SectionCard title="Consejos de Reserva" icon="📅" collapsible={true} defaultCollapsed={true}>
            <p className="booking-tips-text">{(property as any).booking_tips}</p>
          </SectionCard>
        )}

        {/* Source Information */}
        <SectionCard title="Información de la Fuente" icon="🔗" collapsible={true} defaultCollapsed={true}>
          <FieldRenderer label="URL" value={property.url || (property as any).source_url} type="url" icon="🌐" />
          <FieldRenderer label="Tipo de Página" value={(property as any).page_type} icon="📄" />
        </SectionCard>
      </>
    );
  }

  // Original individual tour view
  return (
    <>
      {/* Basic Information */}
      <SectionCard title="Información del Tour" icon="🎯">
        <FieldRenderer 
          label="Nombre" 
          value={(property as any).tour_name || (property as any).property_name || property.title} 
          icon="🎪" 
        />
        <FieldRenderer 
          label="Ubicación" 
          value={(property as any).location} 
          icon="📍" 
        />
        <FieldRenderer 
          label="URL" 
          value={(property as any).source_url || property.url} 
          type="url" 
          icon="🔗" 
        />
        {(property as any).tour_type && (
          <FieldRenderer 
            label="Tipo de Tour" 
            value={(property as any).tour_type} 
            icon="🏷️" 
          />
        )}
        {(property as any).duration_hours && (
          <FieldRenderer 
            label="Duración" 
            value={`${(property as any).duration_hours} horas`} 
            icon="⏱️" 
          />
        )}
        {(property as any).difficulty_level && (
          <FieldRenderer 
            label="Dificultad" 
            value={(property as any).difficulty_level} 
            icon="💪" 
          />
        )}
      </SectionCard>

      {/* Description */}
      {((property as any).description || property.description) && (
        <SectionCard title="Descripción del Tour" icon="📄">
          <div className="description-text" style={{ lineHeight: '1.7', color: '#4A5568' }}>
            {cleanMarkdown((property as any).description || property.description)}
          </div>
        </SectionCard>
      )}
      
      {/* Web Search Context - Clean display */}
      {(property as any).web_search_context && (
        <SectionCard title="Información Adicional" icon="🌐" collapsible={true} defaultCollapsed={true}>
          <div className="web-search-context" style={{ 
            fontSize: '0.95em', 
            color: '#4A5568',
            lineHeight: '1.8',
            padding: '12px',
            background: '#F7FAFC',
            borderRadius: '8px',
            borderLeft: '3px solid #4299E1'
          }}>
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {cleanMarkdown((property as any).web_search_context)}
            </div>
          </div>
        </SectionCard>
      )}

      {/* Pricing */}
      {((property as any).price_usd || (property as any).price_details || property.price_details) && (
        <SectionCard title="Precios" icon="💰">
          {(property as any).price_usd && (
            <FieldRenderer 
              label="Precio" 
              value={`$${(property as any).price_usd} USD`} 
              icon="💵" 
            />
          )}
          {((property as any).price_details || property.price_details) && (
            <div className="price-details" style={{ 
              padding: '12px', 
              background: '#F7FAFC', 
              borderRadius: '6px',
              borderLeft: '3px solid #48BB78'
            }}>
              <p style={{ margin: 0, color: '#2D3748', lineHeight: '1.6' }}>
                {(property as any).price_details || property.price_details}
              </p>
            </div>
          )}
        </SectionCard>
      )}

      {/* Schedule - Updated to show schedules array */}
      {((property as any).schedules || property.tour_schedule) && (
        <SectionCard title="Horarios" icon="📅">
          {(property as any).schedules && Array.isArray((property as any).schedules) ? (
            <div className="schedules-list">
              {(property as any).schedules.map((schedule: string, index: number) => (
                <FieldRenderer 
                  key={index}
                  label={`Horario ${index + 1}`} 
                  value={schedule} 
                  icon="🕐" 
                />
              ))}
            </div>
          ) : (
            property.tour_schedule && <TourSchedule schedule={property.tour_schedule} />
          )}
          {(property as any).check_in_time && (
            <FieldRenderer 
              label="Check-in" 
              value={(property as any).check_in_time} 
              icon="⏰" 
            />
          )}
        </SectionCard>
      )}
      
      {/* What to Bring - Clean display */}
      {(property as any).what_to_bring && Array.isArray((property as any).what_to_bring) && (
        <SectionCard title="Qué Llevar" icon="🎒">
          <div className="what-to-bring-list" style={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: '8px',
            marginTop: '8px'
          }}>
            {(property as any).what_to_bring.map((item: string, index: number) => (
              <span 
                key={index} 
                className="bring-item-badge"
                style={{
                  padding: '6px 12px',
                  background: '#EDF2F7',
                  borderRadius: '6px',
                  fontSize: '0.9em',
                  color: '#2D3748',
                  border: '1px solid #CBD5E0'
                }}
              >
                {item}
              </span>
            ))}
          </div>
        </SectionCard>
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

      {/* Inclusions/Exclusions - Clean list */}
      {((property as any).included_items || (property as any).excluded_items || property.inclusions || property.exclusions) && (
        <SectionCard title="Incluye / No Incluye" icon="✅">
          {((property as any).included_items || property.inclusions) && (
            <div className="inclusions-section" style={{ marginBottom: '16px' }}>
              <h4 style={{ color: '#38A169', fontSize: '1em', marginBottom: '8px' }}>✅ Incluye</h4>
              <ul style={{ 
                margin: 0, 
                paddingLeft: '20px',
                listStyle: 'none'
              }}>
                {(Array.isArray((property as any).included_items) 
                  ? (property as any).included_items 
                  : property.inclusions
                ).map((item: string, index: number) => (
                  <li 
                    key={index}
                    style={{
                      padding: '6px 0',
                      color: '#2D3748',
                      borderBottom: '1px solid #E2E8F0'
                    }}
                  >
                    <span style={{ color: '#38A169', marginRight: '8px' }}>•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {((property as any).excluded_items || property.exclusions) && (
            <div className="exclusions-section">
              <h4 style={{ color: '#E53E3E', fontSize: '1em', marginBottom: '8px' }}>❌ No Incluye</h4>
              <ul style={{ 
                margin: 0, 
                paddingLeft: '20px',
                listStyle: 'none'
              }}>
                {(Array.isArray((property as any).excluded_items) 
                  ? (property as any).excluded_items 
                  : property.exclusions
                ).map((item: string, index: number) => (
                  <li 
                    key={index}
                    style={{
                      padding: '6px 0',
                      color: '#2D3748',
                      borderBottom: '1px solid #E2E8F0'
                    }}
                  >
                    <span style={{ color: '#E53E3E', marginRight: '8px' }}>•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </SectionCard>
      )}
      
      {/* Requirements & Restrictions - NEW */}
      {((property as any).minimum_age || (property as any).max_participants || (property as any).restrictions || property.requirements) && (
        <SectionCard title="Requisitos y Restricciones" icon="⚠️">
          {(property as any).minimum_age && (
            <FieldRenderer 
              label="Edad Mínima" 
              value={`${(property as any).minimum_age} años`} 
              icon="👶" 
            />
          )}
          {(property as any).max_participants && (
            <FieldRenderer 
              label="Máximo de Participantes" 
              value={(property as any).max_participants} 
              icon="👥" 
            />
          )}
          {(property as any).restrictions && (
            <div className="restrictions-text">
              <p>{(property as any).restrictions}</p>
            </div>
          )}
          {property.requirements && Array.isArray(property.requirements) && (
            <FieldRenderer
              label="Requisitos"
              value=""
              type="list"
              listItems={property.requirements}
            />
          )}
        </SectionCard>
      )}
      
      {/* Additional Info - NEW */}
      {((property as any).languages_available || (property as any).pickup_included || (property as any).cancellation_policy) && (
        <SectionCard title="Información Adicional" icon="ℹ️">
          {(property as any).languages_available && (
            <FieldRenderer 
              label="Idiomas Disponibles" 
              value={Array.isArray((property as any).languages_available) 
                ? (property as any).languages_available.join(', ') 
                : (property as any).languages_available
              } 
              icon="🗣️" 
            />
          )}
          {(property as any).pickup_included !== undefined && (
            <FieldRenderer 
              label="Incluye Transporte" 
              value={(property as any).pickup_included ? 'Sí' : 'No'} 
              icon="🚐" 
            />
          )}
          {(property as any).cancellation_policy && (
            <div className="cancellation-policy">
              <strong>📋 Política de Cancelación:</strong>
              <p>{(property as any).cancellation_policy}</p>
            </div>
          )}
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
    </>
  );
};
