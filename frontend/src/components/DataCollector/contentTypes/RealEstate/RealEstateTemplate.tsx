import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { RealEstateDetails } from './RealEstateDetails';

/**
 * Props for RealEstateTemplate component
 */
interface RealEstateTemplateProps {
  /** Property data for real estate */
  property: PropertyData;
}

/**
 * Template component for displaying real estate property data
 * Organizes property information in a structured, user-friendly layout
 * Supports both SPECIFIC properties and GENERAL market guides
 * 
 * @component
 * @example
 * ```tsx
 * <RealEstateTemplate property={propertyData} />
 * ```
 */
export const RealEstateTemplate: React.FC<RealEstateTemplateProps> = ({ property }) => {
  // Check if this is a general market guide page
  const isGeneralGuide = (property as any).page_type === 'general' || 
                         (property as any).page_type === 'general_guide';

  // Render general market guide
  if (isGeneralGuide) {
    const data = property as any;
    
    return (
      <div className="real-estate-template content-template general-guide space-y-6">
        {/* Header Section with Destination */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
          <h2 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
            <span className="text-4xl">🏘️</span>
            {data.destination || 'Guía de Mercado Inmobiliario'}
          </h2>
          {data.overview && (
            <p className="text-gray-700 leading-relaxed mt-4 bg-white/60 p-4 rounded-md">
              {data.overview}
            </p>
          )}
        </div>

        {/* Key Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Properties */}
          {data.total_properties_mentioned && (
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 font-medium">Total Propiedades</p>
                  <p className="text-3xl font-bold text-gray-800 mt-1">
                    {data.total_properties_mentioned.toLocaleString()}
                  </p>
                </div>
                <span className="text-5xl opacity-20">📊</span>
              </div>
            </div>
          )}

          {/* Price Range */}
          {data.price_range && (
            <>
              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-medium">Precio Mínimo</p>
                    <p className="text-2xl font-bold text-gray-800 mt-1">
                      ${data.price_range.min_usd?.toLocaleString() || '0'}
                    </p>
                  </div>
                  <span className="text-5xl opacity-20">💵</span>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-medium">Precio Máximo</p>
                    <p className="text-2xl font-bold text-gray-800 mt-1">
                      ${data.price_range.max_usd?.toLocaleString() || '0'}
                    </p>
                  </div>
                  <span className="text-5xl opacity-20">💰</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Property Types */}
        {data.property_types_available && data.property_types_available.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">🏗️</span>
              Tipos de Propiedades Disponibles
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.property_types_available.map((type: string, idx: number) => (
                <span
                  key={idx}
                  className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium hover:bg-blue-200 transition-colors"
                >
                  {type}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Popular Areas */}
        {data.popular_areas && data.popular_areas.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">🌆</span>
              Áreas Populares
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {data.popular_areas.map((area: string, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200"
                >
                  <span className="text-2xl">📍</span>
                  <span className="font-medium text-gray-700">{area}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Market Trends */}
        {data.market_trends && (
          <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-6 rounded-lg border border-orange-200">
            <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-2xl">📈</span>
              Tendencias del Mercado
            </h3>
            <p className="text-gray-700 leading-relaxed">{data.market_trends}</p>
          </div>
        )}

        {/* Featured Properties */}
        {data.featured_properties && data.featured_properties.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">⭐</span>
              Propiedades Destacadas
              <span className="ml-auto text-sm font-normal text-gray-500">
                ({data.featured_items_count || data.featured_properties.length})
              </span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.featured_properties.map((featuredProp: any, index: number) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-all hover:border-blue-300"
                >
                  <h4 className="font-bold text-gray-800 mb-3 text-lg line-clamp-2">
                    {featuredProp.name || featuredProp.title}
                  </h4>
                  {featuredProp.price_usd && (
                    <div className="flex items-center gap-2 mb-2 text-green-600 font-bold text-xl">
                      <span>💰</span>
                      <span>${featuredProp.price_usd.toLocaleString()}</span>
                    </div>
                  )}
                  {featuredProp.type && (
                    <div className="flex items-center gap-2 mb-2 text-gray-600">
                      <span>🏷️</span>
                      <span className="text-sm">{featuredProp.type}</span>
                    </div>
                  )}
                  {featuredProp.highlight && (
                    <div className="flex items-start gap-2 mt-3 bg-yellow-50 p-3 rounded-md border border-yellow-200">
                      <span>✨</span>
                      <span className="text-sm text-gray-700">{featuredProp.highlight}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Investment Tips */}
        {data.investment_tips && data.investment_tips.length > 0 && (
          <div className="bg-green-50 p-6 rounded-lg border border-green-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">💡</span>
              Consejos de Inversión
            </h3>
            <ul className="space-y-3">
              {data.investment_tips.map((tip: string, idx: number) => (
                <li key={idx} className="flex items-start gap-3 bg-white p-3 rounded-md">
                  <span className="text-green-600 font-bold text-lg mt-0.5">{idx + 1}.</span>
                  <span className="text-gray-700">{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Legal Considerations */}
        {data.legal_considerations && data.legal_considerations.length > 0 && (
          <div className="bg-red-50 p-6 rounded-lg border border-red-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">⚖️</span>
              Consideraciones Legales
            </h3>
            <ul className="space-y-3">
              {data.legal_considerations.map((consideration: string, idx: number) => (
                <li key={idx} className="flex items-start gap-3 bg-white p-3 rounded-md">
                  <span className="text-red-600 text-xl mt-0.5">⚠️</span>
                  <span className="text-gray-700">{consideration}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // Render specific property (original code)
  return (
    <div className="real-estate-template content-template">
      {/* Basic Information */}
      <SectionCard title="Información Básica" icon="📋">
        <FieldRenderer label="Título" value={property.title} icon="🏠" />
        <FieldRenderer label="URL" value={property.url} type="url" icon="🔗" />
        <FieldRenderer label="Categoría" value={property.category} icon="🏷️" />
      </SectionCard>

      {/* Price Details */}
      {property.price_details && (
        <SectionCard title="Detalles de Precio" icon="💰">
          <FieldRenderer
            label="Precio de Venta"
            value={property.price_details.display_price || property.price_details.sale_price}
            type="currency"
            icon="💵"
          />
          <FieldRenderer
            label="Precio de Renta"
            value={property.price_details.rental_price}
            type="currency"
            icon="🏠"
          />
          <FieldRenderer
            label="Moneda"
            value={property.price_details.currency}
            icon="💱"
          />
        </SectionCard>
      )}

      {/* Property Details */}
      {property.details && (
        <RealEstateDetails details={property.details} />
      )}

      {/* Location */}
      {property.location && typeof property.location === 'object' && (
        <SectionCard title="Ubicación" icon="📍">
          <FieldRenderer
            label="Dirección"
            value={property.location.address}
            icon="🏢"
          />
          <FieldRenderer label="Ciudad" value={property.location.city} icon="🌆" />
          <FieldRenderer
            label="Estado/Provincia"
            value={property.location.state}
            icon="🗺️"
          />
          <FieldRenderer label="País" value={property.location.country} icon="🌍" />
          <FieldRenderer
            label="Código Postal"
            value={property.location.postal_code}
            icon="📮"
          />
        </SectionCard>
      )}

      {/* Description */}
      {property.description && (
        <SectionCard title="Descripción" icon="📄">
          <div className="description-text">{property.description}</div>
        </SectionCard>
      )}

      {/* Features */}
      {property.features && property.features.length > 0 && (
        <SectionCard title="Características y Amenidades" icon="⭐">
          <FieldRenderer
            label="Características"
            value=""
            type="list"
            listItems={property.features}
          />
        </SectionCard>
      )}

      {/* Images */}
      {property.images && property.images.length > 0 && (
        <SectionCard title={`Galería de Imágenes (${property.images.length})`} icon="📷">
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
    </div>
  );
};
