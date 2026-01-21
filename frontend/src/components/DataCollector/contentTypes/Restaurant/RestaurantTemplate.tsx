import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { RestaurantMenu } from './RestaurantMenu';

/**
 * Props for RestaurantTemplate component
 */
interface RestaurantTemplateProps {
  /** Property data for restaurant */
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
 * Template component for displaying restaurant information
 * Organizes restaurant details including menu, hours, and amenities
 * 
 * @component
 * @example
 * ```tsx
 * <RestaurantTemplate property={restaurantData} />
 * ```
 */
export const RestaurantTemplate: React.FC<RestaurantTemplateProps> = ({ property }) => {
  const extendedProperty = property as any;
  
  return (
    <div className="restaurant-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información del Restaurante" icon="🍽️">
        <FieldRenderer label="Nombre" value={property.title || extendedProperty.restaurant_name} icon="🏪" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer label="Tipo de Cocina" value={property.cuisine_type || extendedProperty.cuisine_type} icon="👨‍🍳" />
        <FieldRenderer label="Rango de Precio" value={extendedProperty.price_range} icon="💰" />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
      </SectionCard>

      {/* Contact Information - Move up for visibility */}
      {(property.contact || extendedProperty.contact_phone) && (
        <SectionCard title="Información de Contacto" icon="📞">
          {property.contact?.name && <FieldRenderer label="Nombre" value={property.contact.name} icon="👤" />}
          {(property.contact?.phone || extendedProperty.contact_phone) && (
            <FieldRenderer
              label="Teléfono"
              value={property.contact?.phone || extendedProperty.contact_phone}
              type="tel"
              icon="☎️"
            />
          )}
          {property.contact?.email && (
            <FieldRenderer
              label="Email"
              value={property.contact.email}
              type="email"
              icon="📧"
            />
          )}
          {property.contact?.whatsapp && (
            <FieldRenderer
              label="WhatsApp"
              value={property.contact.whatsapp}
              type="tel"
              icon="💬"
            />
          )}
        </SectionCard>
      )}

      {/* Reservations */}
      {(extendedProperty.reservation_required !== undefined || extendedProperty.reservations_required !== undefined) && (
        <SectionCard title="Reservaciones" icon="📅">
          <FieldRenderer 
            label="Reservación Requerida" 
            value={extendedProperty.reservation_required || extendedProperty.reservations_required ? 'Sí' : 'No'} 
            icon="✓" 
          />
        </SectionCard>
      )}

      {/* Operating Hours */}
      {(property.operating_hours || extendedProperty.opening_hours) && (
        <SectionCard title="Horarios de Atención" icon="🕐">
          <div className="operating-hours">
            {Object.entries(property.operating_hours || extendedProperty.opening_hours).map(([day, hours]) => {
              const dayTranslations: { [key: string]: string } = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
              };
              const translatedDay = dayTranslations[day] || day;
              const hoursDisplay = Array.isArray(hours) ? hours.join(', ') : hours;
              
              return (
                <FieldRenderer
                  key={day}
                  label={translatedDay}
                  value={hoursDisplay as string}
                  icon="📅"
                />
              );
            })}
          </div>
        </SectionCard>
      )}

      {/* Description */}
      {property.description && (
        <SectionCard title="Descripción" icon="📄">
          <div className="description-text" style={{ lineHeight: '1.7', color: '#4A5568' }}>
            {cleanMarkdown(property.description)}
          </div>
        </SectionCard>
      )}

      {/* Atmosphere & Ambiance */}
      {extendedProperty.atmosphere && (
        <SectionCard title="Ambiente" icon="🎭">
          <div className="atmosphere-text" style={{ lineHeight: '1.7', color: '#4A5568' }}>
            {cleanMarkdown(extendedProperty.atmosphere)}
          </div>
        </SectionCard>
      )}

      {/* Signature Dishes */}
      {extendedProperty.signature_dishes && (
        <SectionCard title="Platos Destacados" icon="⭐">
          <div className="signature-dishes-text" style={{ lineHeight: '1.7', color: '#4A5568' }}>
            {cleanMarkdown(extendedProperty.signature_dishes)}
          </div>
        </SectionCard>
      )}

      {/* Dietary Options */}
      {extendedProperty.dietary_options && (
        <SectionCard title="Opciones Dietéticas" icon="🥗">
          <div className="dietary-options-text" style={{ lineHeight: '1.7', color: '#4A5568' }}>
            {typeof extendedProperty.dietary_options === 'string' 
              ? cleanMarkdown(extendedProperty.dietary_options)
              : Array.isArray(extendedProperty.dietary_options)
                ? extendedProperty.dietary_options.join(', ')
                : JSON.stringify(extendedProperty.dietary_options)
            }
          </div>
        </SectionCard>
      )}

      {/* Dress Code */}
      {extendedProperty.dress_code && (
        <SectionCard title="Código de Vestimenta" icon="👔">
          <FieldRenderer label="Vestimenta" value={extendedProperty.dress_code} icon="👕" />
        </SectionCard>
      )}

      {/* Web Search Context - Additional Info */}
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

      {/* Price Range */}
      {(property.price_details || extendedProperty.price_details) && (
        <SectionCard title="Detalles de Precios" icon="💰">
          {property.price_details?.display_price && (
            <FieldRenderer
              label="Rango de Precios"
              value={property.price_details.display_price}
              icon="💵"
            />
          )}
          {property.price_details?.average_price && (
            <FieldRenderer
              label="Precio Promedio"
              value={property.price_details.average_price}
              type="currency"
              icon="💳"
            />
          )}
          {property.price_details?.currency && (
            <FieldRenderer label="Moneda" value={property.price_details.currency} icon="💱" />
          )}
          {extendedProperty.price_details && (
            <>
              {extendedProperty.price_details.appetizers_range && (
                <FieldRenderer label="Entradas" value={extendedProperty.price_details.appetizers_range} icon="🥗" />
              )}
              {extendedProperty.price_details.mains_range && (
                <FieldRenderer label="Platos Fuertes" value={extendedProperty.price_details.mains_range} icon="🍖" />
              )}
              {extendedProperty.price_details.desserts_range && (
                <FieldRenderer label="Postres" value={extendedProperty.price_details.desserts_range} icon="🍰" />
              )}
              {extendedProperty.price_details.drinks_range && (
                <FieldRenderer label="Bebidas" value={extendedProperty.price_details.drinks_range} icon="🍹" />
              )}
              {extendedProperty.price_details.note && (
                <div style={{ marginTop: '12px', fontSize: '0.9em', color: '#718096', fontStyle: 'italic' }}>
                  {extendedProperty.price_details.note}
                </div>
              )}
            </>
          )}
        </SectionCard>
      )}

      {/* Operating Hours */}
      {(property.operating_hours || extendedProperty.opening_hours) && (
        <SectionCard title="Horarios de Atención" icon="🕐">
          <div className="operating-hours">
            {Object.entries(property.operating_hours || extendedProperty.opening_hours).map(([day, hours]) => {
              const dayTranslations: { [key: string]: string } = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
              };
              const translatedDay = dayTranslations[day] || day;
              const hoursDisplay = Array.isArray(hours) ? hours.join(', ') : hours;
              
              return (
                <FieldRenderer
                  key={day}
                  label={translatedDay}
                  value={hoursDisplay as string}
                  icon="📅"
                />
              );
            })}
          </div>
        </SectionCard>
      )}

      {/* Menu */}
      {property.menu_items && property.menu_items.length > 0 && (
        <RestaurantMenu menuItems={property.menu_items} />
      )}

      {/* Location */}
      {(property.location || extendedProperty.location) && (
        <SectionCard title="Ubicación" icon="📍">
          {typeof property.location === 'object' ? (
            <>
              <FieldRenderer
                label="Dirección"
                value={property.location.address}
                icon="🏢"
              />
              <FieldRenderer label="Ciudad" value={property.location.city} icon="🌆" />
              <FieldRenderer label="Estado" value={property.location.state} icon="🗺️" />
              <FieldRenderer label="País" value={property.location.country} icon="🌍" />
            </>
          ) : (
            <FieldRenderer
              label="Dirección"
              value={property.location || extendedProperty.location}
              icon="🏢"
            />
          )}
        </SectionCard>
      )}

      {/* Features & Amenities */}
      {((property.features && property.features.length > 0) || 
        (extendedProperty.amenities && (
          (typeof extendedProperty.amenities === 'string' && extendedProperty.amenities.trim() !== '') ||
          (Array.isArray(extendedProperty.amenities) && extendedProperty.amenities.length > 0) ||
          (typeof extendedProperty.amenities === 'object' && !Array.isArray(extendedProperty.amenities))
        ))) && (
        <SectionCard title="Características y Amenidades" icon="⭐">
          {property.features && property.features.length > 0 && (
            <FieldRenderer
              label="Amenidades"
              value=""
              type="list"
              listItems={property.features}
            />
          )}
          {extendedProperty.amenities && (
            <div className="amenities-text" style={{ lineHeight: '1.7', color: '#4A5568', marginTop: '12px' }}>
              {typeof extendedProperty.amenities === 'string' 
                ? cleanMarkdown(extendedProperty.amenities)
                : Array.isArray(extendedProperty.amenities)
                  ? extendedProperty.amenities.join(', ')
                  : JSON.stringify(extendedProperty.amenities)
              }
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

      {/* Special Experiences (Chef's Table, etc.) */}
      {extendedProperty.special_experiences && (
        <SectionCard title="Experiencias Especiales" icon="✨">
          <div className="special-experiences-text" style={{ lineHeight: '1.7', color: '#4A5568' }}>
            {cleanMarkdown(extendedProperty.special_experiences)}
          </div>
        </SectionCard>
      )}

      {/* Web Search Sources - For transparency */}
      {extendedProperty.web_search_sources && extendedProperty.web_search_sources.length > 0 && (
        <SectionCard title="Fuentes de Información" icon="📚" collapsible={true} defaultCollapsed={true}>
          <div style={{ fontSize: '0.85em', color: '#718096' }}>
            <p style={{ marginBottom: '8px', fontWeight: '500' }}>
              Esta información fue verificada consultando las siguientes fuentes:
            </p>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {extendedProperty.web_search_sources.slice(0, 10).map((source: string, index: number) => {
                const domain = new URL(source).hostname.replace('www.', '');
                return (
                  <li key={index} style={{ marginBottom: '6px' }}>
                    <a 
                      href={source} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ color: '#4299E1', textDecoration: 'none' }}
                    >
                      {domain}
                    </a>
                  </li>
                );
              })}
            </ul>
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
