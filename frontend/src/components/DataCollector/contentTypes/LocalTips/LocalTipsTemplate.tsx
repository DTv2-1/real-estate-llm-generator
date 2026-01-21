import React, { useState } from 'react';
import type { PropertyData } from '../../types';

/**
 * Props for LocalTipsTemplate component
 */
interface LocalTipsTemplateProps {
  /** Property data for local tips */
  property: PropertyData;
}

interface Destination {
  name: string;
  highlights?: string[];
  best_for?: string;
  activities?: string[];
}

const getCategoryColor = (category?: string) => {
  const colors: Record<string, string> = {
    adventure: 'from-orange-500 to-red-500',
    nature: 'from-green-500 to-emerald-600',
    beach: 'from-cyan-500 to-blue-500',
    culture: 'from-purple-500 to-pink-500',
    city: 'from-gray-600 to-slate-700',
    wildlife: 'from-lime-500 to-green-600',
  };
  return colors[category?.toLowerCase() || ''] || 'from-blue-500 to-indigo-600';
};

const getCategoryIcon = (category?: string) => {
  const icons: Record<string, string> = {
    adventure: '🏔️',
    nature: '🌿',
    beach: '🏖️',
    culture: '🏛️',
    city: '🏙️',
    wildlife: '🦜',
  };
  return icons[category?.toLowerCase() || ''] || '📍';
};

/**
 * Modern template component for displaying local tips and travel guides
 */
export const LocalTipsTemplate: React.FC<LocalTipsTemplateProps> = ({ property }) => {
  const [expandedDest, setExpandedDest] = useState<number | null>(null);
  const [showAllSources, setShowAllSources] = useState(false);
  
  // Collapsible sections state - all start collapsed
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    description: false,
    destinations: false,
    budget: false,
    practical: false,
    warnings: false,
    customs: false,
    emergency: false,
    sources: false,
    metadata: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const SectionHeader: React.FC<{
    title: string;
    icon: string;
    count?: number;
    sectionKey: string;
  }> = ({ title, icon, count, sectionKey }) => (
    <button
      onClick={() => toggleSection(sectionKey)}
      className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors rounded-lg group"
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <h2 className="text-xl md:text-2xl font-bold text-gray-900">{title}</h2>
        {count !== undefined && (
          <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm font-bold">
            {count}
          </span>
        )}
      </div>
      <svg
        className={`w-6 h-6 text-gray-400 transition-transform ${expandedSections[sectionKey] ? 'rotate-180' : ''}`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  );
  
  const location = typeof property.location === 'string' 
    ? property.location 
    : property.location?.city || property.location?.country || '';

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-white shadow-2xl">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative p-8 md:p-12">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-semibold mb-4">
                <span>🗺️</span>
                <span>{property.category || 'Guía de Viaje'}</span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
                {property.title || 'Guía de Viaje'}
              </h1>
              {location && (
                <div className="flex items-center gap-2 text-lg text-white/90">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium">{location}</span>
                </div>
              )}
            </div>
            {property.extraction_confidence && (
              <div className="hidden md:block bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{(property.extraction_confidence * 100).toFixed(0)}%</div>
                <div className="text-xs text-white/80 mt-1">Confianza</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content Type & Page Type Info */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="flex flex-col md:flex-row">
          {/* Content Type */}
          {property.content_type && (
            <div className="flex-1 p-6 border-b md:border-b-0 md:border-r border-gray-200">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
                  <span className="text-2xl">
                    {property.content_type === 'local_tips' && '🗺️'}
                    {property.content_type === 'restaurant' && '🍽️'}
                    {property.content_type === 'tour' && '🎯'}
                    {property.content_type === 'transportation' && '🚌'}
                    {property.content_type === 'real_estate' && '🏠'}
                    {!['local_tips', 'restaurant', 'tour', 'transportation', 'real_estate'].includes(property.content_type) && '📄'}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                    Tipo de Contenido
                  </div>
                  <div className="text-lg font-bold text-gray-900">
                    {property.content_type === 'local_tips' && 'Local Tips'}
                    {property.content_type === 'restaurant' && 'Restaurante'}
                    {property.content_type === 'tour' && 'Tour / Actividad'}
                    {property.content_type === 'transportation' && 'Transporte'}
                    {property.content_type === 'real_estate' && 'Bienes Raíces'}
                    {!['local_tips', 'restaurant', 'tour', 'transportation', 'real_estate'].includes(property.content_type) && property.content_type}
                  </div>
                  {property.content_type_confidence !== undefined && (
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-1.5 rounded-full transition-all"
                          style={{ width: `${property.content_type_confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-gray-600">
                        {(property.content_type_confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Page Type */}
          {property.page_type && (
            <div className="flex-1 p-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg">
                  <span className="text-2xl">
                    {property.page_type === 'general' && '📋'}
                    {property.page_type === 'specific' && '📍'}
                    {!['general', 'specific'].includes(property.page_type) && '📄'}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                    Tipo de Página
                  </div>
                  <div className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    {property.page_type === 'general' && (
                      <>
                        <span>General</span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                          Guía Amplia
                        </span>
                      </>
                    )}
                    {property.page_type === 'specific' && (
                      <>
                        <span>Específico</span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-pink-100 text-pink-700">
                          Detalle
                        </span>
                      </>
                    )}
                    {!['general', 'specific'].includes(property.page_type) && property.page_type}
                  </div>
                  <div className="mt-1 text-xs text-gray-600">
                    {property.page_type === 'general' && 'Información general y múltiples destinos'}
                    {property.page_type === 'specific' && 'Información detallada de un lugar específico'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Info Bar */}
      {(property.best_time || property.recommended_duration || property.safety_rating) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {property.best_time && (
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center text-2xl">
                  ☀️
                </div>
                <div className="flex-1">
                  <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Mejor Época</div>
                  <div className="text-sm text-gray-900 font-semibold mt-0.5">{property.best_time}</div>
                </div>
              </div>
            </div>
          )}
          {property.recommended_duration && (
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-2xl">
                  ⏱️
                </div>
                <div className="flex-1">
                  <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Duración</div>
                  <div className="text-sm text-gray-900 font-semibold mt-0.5">{property.recommended_duration}</div>
                </div>
              </div>
            </div>
          )}
          {property.safety_rating && (
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-2xl">
                  🛡️
                </div>
                <div className="flex-1">
                  <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Seguridad</div>
                  <div className="text-sm text-gray-900 font-semibold mt-0.5">{property.safety_rating}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Description */}
      {property.description && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <SectionHeader title="Descripción General" icon="📖" sectionKey="description" />
          {expandedSections.description && (
            <div className="p-6 pt-0 border-t border-gray-100">
              <p className="text-gray-700 leading-relaxed text-lg">
                {property.description}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Destinations Grid - Modern Card Design */}
      {property.destinations_covered && property.destinations_covered.length > 0 && (
        <div className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              title="Destinos Destacados" 
              icon="🏝️" 
              count={property.destinations_covered.length}
              sectionKey="destinations"
            />
          </div>
          
          {expandedSections.destinations && (
            <div className="px-6 pb-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {property.destinations_covered.map((dest: Destination, index: number) => {
              const gradient = getCategoryColor(dest.best_for);
              const icon = getCategoryIcon(dest.best_for);
              const isExpanded = expandedDest === index;
              
              return (
                <div
                  key={index}
                  className="group bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 border border-gray-200 hover:border-indigo-300"
                >
                  {/* Card Header */}
                  <div className={`bg-gradient-to-r ${gradient} p-5 text-white relative`}>
                    <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
                      <div className="text-8xl">{icon}</div>
                    </div>
                    <div className="relative">
                      <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">
                        <span>{icon}</span>
                        {dest.name}
                      </h3>
                      {dest.best_for && (
                        <span className="inline-block bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide">
                          {dest.best_for}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Card Body */}
                  <div className="p-5 space-y-4">
                    {/* Highlights */}
                    {dest.highlights && dest.highlights.length > 0 && (
                      <div>
                        <div className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-2">
                          <span>✨</span>
                          Highlights
                        </div>
                        <ul className="space-y-2">
                          {dest.highlights.slice(0, isExpanded ? undefined : 3).map((highlight: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-gray-700">
                              <span className="text-indigo-500 mt-1">•</span>
                              <span className="flex-1">{highlight}</span>
                            </li>
                          ))}
                        </ul>
                        {!isExpanded && dest.highlights.length > 3 && (
                          <button
                            onClick={() => setExpandedDest(index)}
                            className="mt-2 text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1"
                          >
                            <span>Ver más ({dest.highlights.length - 3})</span>
                            <span>→</span>
                          </button>
                        )}
                      </div>
                    )}

                    {/* Activities */}
                    {dest.activities && dest.activities.length > 0 && (
                      <div>
                        <div className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-2">
                          <span>🎯</span>
                          Actividades
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {dest.activities.map((activity: string, idx: number) => (
                            <span
                              key={idx}
                              className="inline-flex items-center gap-1 bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 px-3 py-1.5 rounded-lg text-xs font-medium border border-indigo-200 hover:from-indigo-100 hover:to-purple-100 transition-colors"
                            >
                              {activity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
            </div>
          )}
        </div>
      )}

      {/* Budget Guide - Premium Design */}
      {property.budget_guide && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <SectionHeader title="Guía de Presupuesto" icon="💰" sectionKey="budget" />
          
          {expandedSections.budget && (
            <div className="p-6 pt-0 border-t border-gray-100">
            {property.budget_guide.budget && (
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-400 to-green-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition"></div>
                <div className="relative bg-white rounded-2xl p-6 border-2 border-emerald-300 hover:border-emerald-400 transition-all shadow-lg">
                  <div className="w-14 h-14 bg-gradient-to-br from-emerald-100 to-green-100 rounded-full flex items-center justify-center text-3xl mb-4 mx-auto">
                    🎒
                  </div>
                  <h3 className="text-center font-bold text-gray-700 text-sm uppercase tracking-wide mb-2">
                    Mochilero
                  </h3>
                  <p className="text-center text-2xl font-bold text-emerald-600">
                    {property.budget_guide.budget}
                  </p>
                </div>
              </div>
            )}
            
            {property.budget_guide.mid_range && (
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition"></div>
                <div className="relative bg-white rounded-2xl p-6 border-2 border-blue-300 hover:border-blue-400 transition-all shadow-lg">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center text-3xl mb-4 mx-auto">
                    🏨
                  </div>
                  <h3 className="text-center font-bold text-gray-700 text-sm uppercase tracking-wide mb-2">
                    Rango Medio
                  </h3>
                  <p className="text-center text-2xl font-bold text-blue-600">
                    {property.budget_guide.mid_range}
                  </p>
                </div>
              </div>
            )}
            
            {property.budget_guide.luxury && (
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-400 to-pink-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition"></div>
                <div className="relative bg-white rounded-2xl p-6 border-2 border-purple-300 hover:border-purple-400 transition-all shadow-lg">
                  <div className="w-14 h-14 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center text-3xl mb-4 mx-auto">
                    💎
                  </div>
                  <h3 className="text-center font-bold text-gray-700 text-sm uppercase tracking-wide mb-2">
                    Lujo
                  </h3>
                  <p className="text-center text-2xl font-bold text-purple-600">
                    {property.budget_guide.luxury}
                  </p>
                </div>
              </div>
            )}
          
            {property.budget_guide.notes && (
              <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200">
                <p className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-lg">💡</span>
                  <span>{property.budget_guide.notes}</span>
                </p>
              </div>
            )}
          </div>
          )}
        </div>
      )}

      {/* Practical Info & Essentials - Collapsible Grid */}
      {(property.practical_advice || property.transportation_tips || property.visa_info || 
        property.language || property.currency || property.cost_estimate) && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <SectionHeader title="Información Práctica" icon="💡" sectionKey="practical" />
          
          {expandedSections.practical && (
            <div className="p-6 pt-0 border-t border-gray-100">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Practical Advice */}
        {property.practical_advice && (
          <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl p-6 border border-amber-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">💡</span>
              Consejos Prácticos
            </h3>
            <p className="text-gray-700 leading-relaxed">{property.practical_advice}</p>
          </div>
        )}

        {/* Transportation */}
        {property.transportation_tips && (
          <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 border border-indigo-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">🚌</span>
              Transporte
            </h3>
            <p className="text-gray-700 leading-relaxed">{property.transportation_tips}</p>
          </div>
        )}

        {/* Visa Info */}
        {property.visa_info && (
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">🛂</span>
              Visa & Requisitos
            </h3>
            <p className="text-gray-700 leading-relaxed">{property.visa_info}</p>
          </div>
        )}

        {/* Language */}
        {property.language && (
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">💬</span>
              Idioma
            </h3>
            <p className="text-gray-700 leading-relaxed">{property.language}</p>
          </div>
        )}

        {/* Currency */}
        {property.currency && (
          <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl p-6 border border-yellow-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">💵</span>
              Moneda
            </h3>
            <p className="text-gray-700 leading-relaxed">{property.currency}</p>
          </div>
        )}

        {/* Cost Estimate */}
        {property.cost_estimate && (
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">💸</span>
              Costos Estimados
            </h3>
            <p className="text-gray-700 leading-relaxed">{property.cost_estimate}</p>
          </div>
        )}
      </div>
            </div>
          )}
        </div>
      )}

      {/* Important Lists - Warning & Culture */}
      {((property.things_to_avoid && property.things_to_avoid.length > 0) || 
        (property.local_customs && property.local_customs.length > 0)) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Things to Avoid */}
        {property.things_to_avoid && property.things_to_avoid.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <SectionHeader 
              title="Cosas a Evitar" 
              icon="⚠️" 
              count={property.things_to_avoid.length}
              sectionKey="warnings"
            />
            {expandedSections.warnings && (
              <div className="p-6 pt-0 border-t border-gray-100">
                <ul className="space-y-2">
                  {property.things_to_avoid.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-3">
                      <span className="text-red-500 mt-1 font-bold">×</span>
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Local Customs */}
        {property.local_customs && property.local_customs.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <SectionHeader 
              title="Costumbres Locales" 
              icon="🤝" 
              count={property.local_customs.length}
              sectionKey="customs"
            />
            {expandedSections.customs && (
              <div className="p-6 pt-0 border-t border-gray-100">
                <ul className="space-y-2">
                  {property.local_customs.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-3">
                      <span className="text-purple-500 mt-1">✓</span>
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
      )}

      {/* Emergency Contacts */}
      {property.emergency_contacts && property.emergency_contacts.length > 0 && (
        <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl shadow-sm border border-red-200 overflow-hidden">
          <SectionHeader 
            title="Contactos de Emergencia" 
            icon="🚨" 
            count={property.emergency_contacts.length}
            sectionKey="emergency"
          />
          {expandedSections.emergency && (
            <div className="p-6 pt-0 border-t border-red-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {property.emergency_contacts.map((contact: any, index: number) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-red-200 hover:border-red-300 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <span className="text-xl">📞</span>
                  </div>
                  <div className="flex-1">
                    {typeof contact === 'string' ? (
                      <p className="font-medium text-gray-800">{contact}</p>
                    ) : (
                      <>
                        <p className="font-semibold text-gray-900">{contact.service || contact.name}</p>
                        <p className="text-sm text-gray-600">{contact.number || contact.phone}</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Web Search Sources - Modern Link Cards */}
      {property.web_search_sources && property.web_search_sources.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <SectionHeader 
            title="Fuentes de Información" 
            icon="📚" 
            count={property.web_search_sources.length}
            sectionKey="sources"
          />
          
          {expandedSections.sources && (
            <div className="p-6 pt-0 border-t border-gray-100">
              <div className="grid grid-cols-1 gap-3">
                {property.web_search_sources
              .slice(0, showAllSources ? undefined : 8)
              .map((source: string, index: number) => {
                const domain = new URL(source).hostname.replace('www.', '');
                return (
                  <a
                    key={index}
                    href={source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-white hover:from-blue-50 hover:to-indigo-50 rounded-xl border border-gray-200 hover:border-blue-300 transition-all hover:shadow-md"
                  >
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                      🔗
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 font-medium mb-0.5">{domain}</p>
                      <p className="text-sm text-gray-700 group-hover:text-blue-600 truncate transition-colors">
                        {source}
                      </p>
                    </div>
                    <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                );
              })}
              </div>
          
              {property.web_search_sources.length > 8 && (
                <div className="mt-4 text-center">
                  <button
                    onClick={() => setShowAllSources(!showAllSources)}
                    className="inline-flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium rounded-lg shadow-sm hover:shadow-md transition-all"
                  >
                    <span>{showAllSources ? 'Ver menos' : `Ver todas (${property.web_search_sources.length})`}</span>
                    <svg className={`w-4 h-4 transition-transform ${showAllSources ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Source Metadata - Clean Info Card */}
      <div className="bg-gradient-to-br from-gray-50 to-slate-100 rounded-2xl border border-gray-200 overflow-hidden">
        <SectionHeader title="Metadata de Extracción" icon="ℹ️" sectionKey="metadata" />
        
        {expandedSections.metadata && (
          <div className="p-6 pt-0 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wide">URL Original</div>
                <a 
                  href={property.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-700 truncate block"
                >
                  {property.source_url}
                </a>
              </div>
          
              {property.content_type && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wide">Tipo de Contenido</div>
                  <div className="text-sm font-semibold text-gray-900">{property.content_type}</div>
                </div>
              )}
          
              {property.page_type && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wide">Tipo de Página</div>
                  <div className="text-sm font-semibold text-gray-900">{property.page_type}</div>
                </div>
              )}
          
              {property.extraction_confidence !== undefined && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wide">Confianza de Extracción</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full transition-all"
                        style={{ width: `${property.extraction_confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-bold text-gray-900">
                      {(property.extraction_confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

    </div>
  );
};
