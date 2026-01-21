import React from 'react';
import type { PropertyData } from '../../types';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';
import { RestaurantMenu } from './RestaurantMenu';
import {
  RestaurantIcon,
  PhoneIcon,
  LocationIcon,
  DollarIcon,
  ClockIcon,
  StarIcon,
  FileTextIcon,
  SparklesIcon,
  UsersIcon,
  LeafIcon,
  ChefHatIcon,
  BookOpenIcon,
  GlobeIcon,
  LinkIcon,
  TagIcon,
  AwardIcon
} from '../../icons/RestaurantIcons';

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
 * Format opening hours object into readable format
 */
const formatOpeningHours = (hours: any): { day: string; hours: string }[] => {
  if (!hours || typeof hours !== 'object') return [];
  
  const dayTranslations: { [key: string]: string } = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
  };
  
  const dayOrder = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  
  return dayOrder
    .filter(day => hours[day])
    .map(day => {
      const dayHours = hours[day];
      let hoursText = '';
      
      if (typeof dayHours === 'object' && dayHours.opens && dayHours.closes) {
        hoursText = `${dayHours.opens} - ${dayHours.closes}`;
      } else if (typeof dayHours === 'string') {
        hoursText = dayHours;
      } else if (Array.isArray(dayHours)) {
        hoursText = dayHours.join(', ');
      }
      
      return {
        day: dayTranslations[day] || day,
        hours: hoursText
      };
    });
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
  const openingHours = formatOpeningHours(property.operating_hours || extendedProperty.opening_hours);
  
  return (
    <div className="restaurant-template content-template space-y-6">
      {/* Hero Header with Restaurant Name */}
      <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-6 border-l-4 border-orange-500">
        <div className="flex items-center gap-3 mb-2">
          <RestaurantIcon className="text-orange-600" size={32} />
          <h1 className="text-3xl font-bold text-gray-900">
            {property.title || extendedProperty.restaurant_name}
          </h1>
        </div>
        {extendedProperty.cuisine_type && (
          <div className="flex flex-wrap gap-2 mt-3">
            {(Array.isArray(extendedProperty.cuisine_type) 
              ? extendedProperty.cuisine_type 
              : [extendedProperty.cuisine_type]
            ).map((cuisine: string, idx: number) => (
              <span 
                key={idx}
                className="inline-flex items-center gap-1 px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium"
              >
                <ChefHatIcon size={14} />
                {cuisine}
              </span>
            ))}
          </div>
        )}
        {extendedProperty.rating && (
          <div className="flex items-center gap-2 mt-3">
            <StarIcon className="text-yellow-500" size={24} />
            <span className="text-xl font-semibold text-gray-900">{extendedProperty.rating}</span>
            {extendedProperty.number_of_reviews && (
              <span className="text-gray-600">({extendedProperty.number_of_reviews.toLocaleString()} reseñas)</span>
            )}
          </div>
        )}
      </div>

      {/* Quick Info Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Price Range Card */}
        {extendedProperty.price_range && (
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <DollarIcon className="text-green-600" size={28} />
              <div>
                <div className="text-sm text-gray-600 font-medium">Rango de Precio</div>
                <div className="text-lg font-semibold text-gray-900">{extendedProperty.price_range}</div>
              </div>
            </div>
          </div>
        )}
        
        {/* Phone Card */}
        {extendedProperty.contact_phone && (
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <PhoneIcon className="text-blue-600" size={28} />
              <div>
                <div className="text-sm text-gray-600 font-medium">Teléfono</div>
                <a 
                  href={`tel:${extendedProperty.contact_phone}`}
                  className="text-lg font-semibold text-blue-600 hover:text-blue-800"
                >
                  {extendedProperty.contact_phone}
                </a>
              </div>
            </div>
          </div>
        )}
        
        {/* Location Card */}
        {(property.location || extendedProperty.location) && (
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <LocationIcon className="text-red-600" size={28} />
              <div>
                <div className="text-sm text-gray-600 font-medium">Ubicación</div>
                <div className="text-lg font-semibold text-gray-900">
                  {typeof property.location === 'string' ? property.location : extendedProperty.location}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Description */}
      {property.description && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <FileTextIcon className="text-gray-700" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Descripción</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">
            {cleanMarkdown(property.description)}
          </p>
        </div>
      )}

      {/* Signature Dishes */}
      {extendedProperty.signature_dishes && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border-l-4 border-yellow-500 p-6">
          <div className="flex items-center gap-2 mb-4">
            <AwardIcon className="text-yellow-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Platos Destacados</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">
            {cleanMarkdown(extendedProperty.signature_dishes)}
          </p>
        </div>
      )}

      {/* Atmosphere */}
      {extendedProperty.atmosphere && (
        <div className="bg-purple-50 rounded-lg border-l-4 border-purple-500 p-6">
          <div className="flex items-center gap-2 mb-4">
            <UsersIcon className="text-purple-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Ambiente</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">
            {cleanMarkdown(extendedProperty.atmosphere)}
          </p>
        </div>
      )}

      {/* Operating Hours - Modern Design */}
      {openingHours.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <ClockIcon className="text-blue-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Horarios de Atención</h2>
          </div>
          <div className="space-y-2">
            {openingHours.map(({ day, hours }) => (
              <div key={day} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="font-medium text-gray-700">{day}:</span>
                <span className="text-gray-900 font-semibold">{hours}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Amenities Grid */}
      {extendedProperty.amenities && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <SparklesIcon className="text-indigo-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Características y Amenidades</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {(Array.isArray(extendedProperty.amenities) 
              ? extendedProperty.amenities 
              : typeof extendedProperty.amenities === 'string'
                ? extendedProperty.amenities.split(',').map((a: string) => a.trim())
                : []
            ).map((amenity: string, idx: number) => (
              <span 
                key={idx}
                className="inline-flex items-center gap-1 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium border border-blue-200"
              >
                <TagIcon size={14} />
                {amenity}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Dietary Options */}
      {extendedProperty.dietary_options && (
        <div className="bg-green-50 rounded-lg border-l-4 border-green-500 p-6">
          <div className="flex items-center gap-2 mb-4">
            <LeafIcon className="text-green-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Opciones Dietéticas</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {(Array.isArray(extendedProperty.dietary_options) 
              ? extendedProperty.dietary_options 
              : [extendedProperty.dietary_options]
            ).map((option: string, idx: number) => (
              <span 
                key={idx}
                className="inline-flex items-center gap-1 px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium"
              >
                <LeafIcon size={14} />
                {option}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Price Details - Modern Table */}
      {extendedProperty.price_details && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <DollarIcon className="text-green-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Detalles de Precios</h2>
          </div>
          <div className="space-y-3">
            {extendedProperty.price_details.appetizers_range && (
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <ChefHatIcon className="text-blue-600" size={20} />
                  <span className="font-medium text-gray-700">Entradas:</span>
                </div>
                <span className="text-lg font-bold text-gray-900">{extendedProperty.price_details.appetizers_range}</span>
              </div>
            )}
            {extendedProperty.price_details.mains_range && (
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <RestaurantIcon className="text-orange-600" size={20} />
                  <span className="font-medium text-gray-700">Platos Fuertes:</span>
                </div>
                <span className="text-lg font-bold text-gray-900">{extendedProperty.price_details.mains_range}</span>
              </div>
            )}
            {extendedProperty.price_details.desserts_range && (
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <StarIcon className="text-pink-600" size={20} />
                  <span className="font-medium text-gray-700">Postres:</span>
                </div>
                <span className="text-lg font-bold text-gray-900">{extendedProperty.price_details.desserts_range}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Special Experiences */}
      {extendedProperty.special_experiences && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border-l-4 border-indigo-500 p-6">
          <div className="flex items-center gap-2 mb-4">
            <SparklesIcon className="text-indigo-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Experiencias Especiales</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">
            {cleanMarkdown(extendedProperty.special_experiences)}
          </p>
        </div>
      )}

      {/* Web Search Sources - Collapsible */}
      {extendedProperty.web_search_sources && extendedProperty.web_search_sources.length > 0 && (
        <details className="bg-gray-50 rounded-lg border border-gray-200 p-6">
          <summary className="cursor-pointer flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors">
            <BookOpenIcon className="text-gray-600" size={20} />
            <span>Fuentes de Información ({extendedProperty.web_search_sources.length})</span>
          </summary>
          <div className="mt-4 space-y-2">
            {extendedProperty.web_search_sources.slice(0, 10).map((source: string, index: number) => {
              try {
                const domain = new URL(source).hostname.replace('www.', '');
                return (
                  <a 
                    key={index}
                    href={source} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 p-2 hover:bg-white rounded transition-colors text-blue-600 hover:text-blue-800"
                  >
                    <LinkIcon size={14} />
                    <span className="text-sm">{domain}</span>
                  </a>
                );
              } catch {
                return null;
              }
            })}
          </div>
        </details>
      )}

      {/* Additional Web Context - Collapsible */}
      {(property as any).web_search_context && (
        <details className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <summary className="cursor-pointer flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors">
            <GlobeIcon className="text-blue-600" size={20} />
            <span>Contexto Adicional de la Web</span>
          </summary>
          <div className="mt-4 prose prose-sm max-w-none">
            <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {cleanMarkdown((property as any).web_search_context)}
            </div>
          </div>
        </details>
      )}
    </div>
  );
};
