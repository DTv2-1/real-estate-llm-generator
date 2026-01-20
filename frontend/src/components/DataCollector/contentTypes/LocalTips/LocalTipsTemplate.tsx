import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { LocalTipsCategories } from './LocalTipsCategories';

/**
 * Props for LocalTipsTemplate component
 */
interface LocalTipsTemplateProps {
  /** Property data for local tips */
  property: PropertyData;
}

/**
 * Template component for displaying local tips and recommendations
 * Organizes local advice, recommendations, and practical information
 * 
 * @component
 * @example
 * ```tsx
 * <LocalTipsTemplate property={localTipsData} />
 * ```
 */
export const LocalTipsTemplate: React.FC<LocalTipsTemplateProps> = ({ property }) => {
  return (
    <div className="local-tips-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información General" icon="💡">
        <FieldRenderer label="Título" value={property.title} icon="📌" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
        <FieldRenderer label="Tipo de Tip" value={property.tip_type} icon="🎯" />
      </SectionCard>

      {/* Description/Content */}
      {property.description && (
        <SectionCard title="Contenido" icon="📄">
          <div className="description-text">{property.description}</div>
        </SectionCard>
      )}

      {/* Tips by Category */}
      {property.tips_by_category && (
        <LocalTipsCategories tipsByCategory={property.tips_by_category} />
      )}

      {/* Key Points/Highlights */}
      {property.key_points && property.key_points.length > 0 && (
        <SectionCard title="Puntos Clave" icon="⭐">
          <FieldRenderer
            label="Destacados"
            value=""
            type="list"
            listItems={property.key_points}
          />
        </SectionCard>
      )}

      {/* Do's and Don'ts */}
      {(property.dos || property.donts) && (
        <SectionCard title="Recomendaciones" icon="✅">
          {property.dos && property.dos.length > 0 && (
            <div className="dos-section">
              <h4 className="subsection-title">✅ Hacer:</h4>
              <FieldRenderer
                label=""
                value=""
                type="list"
                listItems={property.dos}
              />
            </div>
          )}

          {property.donts && property.donts.length > 0 && (
            <div className="donts-section">
              <h4 className="subsection-title">❌ No Hacer:</h4>
              <FieldRenderer
                label=""
                value=""
                type="list"
                listItems={property.donts}
              />
            </div>
          )}
        </SectionCard>
      )}

      {/* Location/Area Specific */}
      {property.location && typeof property.location === 'object' && (
        <SectionCard title="Ubicación" icon="📍">
          <FieldRenderer label="Ciudad" value={property.location.city} icon="🌆" />
          <FieldRenderer label="Estado" value={property.location.state} icon="🗺️" />
          <FieldRenderer label="País" value={property.location.country} icon="🌍" />
        </SectionCard>
      )}

      {/* Best Time to Visit/Do */}
      {property.best_time && (
        <SectionCard title="Mejor Momento" icon="⏰">
          <FieldRenderer
            label="Temporada"
            value={property.best_time.season}
            icon="🌤️"
          />
          <FieldRenderer
            label="Meses"
            value={property.best_time.months}
            icon="📅"
          />
          <FieldRenderer
            label="Hora del Día"
            value={property.best_time.time_of_day}
            icon="🕐"
          />
        </SectionCard>
      )}

      {/* Budget Information */}
      {property.price_details && (
        <SectionCard title="Información de Presupuesto" icon="💰">
          <FieldRenderer
            label="Rango de Precio"
            value={property.price_details.display_price}
            icon="💵"
          />
          <FieldRenderer
            label="Nivel de Precio"
            value={property.price_details.price_level}
            icon="💳"
          />
        </SectionCard>
      )}

      {/* Useful Links */}
      {property.useful_links && property.useful_links.length > 0 && (
        <SectionCard title="Enlaces Útiles" icon="🔗">
          <div className="useful-links">
            {property.useful_links.map((link: any, index: number) => (
              <div key={index} className="link-item">
                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="link-url"
                >
                  {link.title || link.url}
                </a>
                {link.description && (
                  <p className="link-description">{link.description}</p>
                )}
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Images */}
      {property.images && property.images.length > 0 && (
        <SectionCard title={`Imágenes (${property.images.length})`} icon="📷">
          <div className="images-grid">
            {property.images.map((imageUrl: string, index: number) => (
              <div key={index} className="image-thumbnail">
                <img src={imageUrl} alt={`Imagen ${index + 1}`} loading="lazy" />
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Additional Tips */}
      {property.additional_tips && property.additional_tips.length > 0 && (
        <SectionCard title="Tips Adicionales" icon="📝">
          <FieldRenderer
            label="Consejos"
            value=""
            type="list"
            listItems={property.additional_tips}
          />
        </SectionCard>
      )}
    </div>
  );
};
