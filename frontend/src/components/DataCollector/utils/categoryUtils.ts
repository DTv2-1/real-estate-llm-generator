/**
 * Category Utilities
 * 
 * Utilities for categorizing and managing real estate property categories
 */

import type { CategoryConfig } from '../types'

/**
 * Category configurations for real estate properties
 * Maps category keys to display names, icons, and colors
 */
export const CATEGORIES: Record<string, CategoryConfig> = {
  'nuevos-proyectos': {
    id: 'nuevos-proyectos',
    name: 'Proyectos Nuevos',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V8a2 2 0 00-2-2h-5L9 4H4zm7 5a1 1 0 00-2 0v1H8a1 1 0 000 2h1v1a1 1 0 002 0v-1h1a1 1 0 000-2h-1V9z" clip-rule="evenodd"></path></svg>',
    color: '#8b5cf6'
  },
  'venta-casas': {
    id: 'venta-casas',
    name: 'Casas en Venta',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>',
    color: '#10b981'
  },
  'venta-apartamentos': {
    id: 'venta-apartamentos',
    name: 'Apartamentos en Venta',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd"></path></svg>',
    color: '#3b82f6'
  },
  'venta-negocios': {
    id: 'venta-negocios',
    name: 'Negocios en Venta',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"></path><path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z"></path></svg>',
    color: '#f59e0b'
  },
  'venta-lotes': {
    id: 'venta-lotes',
    name: 'Lotes/Terrenos',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path></svg>',
    color: '#059669'
  },
  'venta-fincas': {
    id: 'venta-fincas',
    name: 'Fincas en Venta',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 3.5a1.5 1.5 0 013 0V4a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-.5a1.5 1.5 0 000 3h.5a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-.5a1.5 1.5 0 00-3 0v.5a1 1 0 01-1 1H6a1 1 0 01-1-1v-3a1 1 0 00-1-1h-.5a1.5 1.5 0 010-3H4a1 1 0 001-1V6a1 1 0 011-1h3a1 1 0 001-1v-.5z"></path></svg>',
    color: '#84cc16'
  },
  'alquiler-casas': {
    id: 'alquiler-casas',
    name: 'Casas en Alquiler',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path><path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z"></path></svg>',
    color: '#06b6d4'
  },
  'alquiler-apartamentos': {
    id: 'alquiler-apartamentos',
    name: 'Apartamentos en Alquiler',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M11 17a1 1 0 001.447.894l4-2A1 1 0 0017 15V9.236a1 1 0 00-1.447-.894l-4 2a1 1 0 00-.553.894V17zM15.211 6.276a1 1 0 000-1.788l-4.764-2.382a1 1 0 00-.894 0L4.789 4.488a1 1 0 000 1.788l4.764 2.382a1 1 0 00.894 0l4.764-2.382zM4.447 8.342A1 1 0 003 9.236V15a1 1 0 00.553.894l4 2A1 1 0 009 17v-5.764a1 1 0 00-.553-.894l-4-2z"></path></svg>',
    color: '#0ea5e9'
  },
  'alquiler-locales': {
    id: 'alquiler-locales',
    name: 'Locales Comerciales',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M13 7H7v6h6V7z"></path><path fill-rule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clip-rule="evenodd"></path></svg>',
    color: '#8b5cf6'
  },
  other: {
    id: 'other',
    name: 'Otros',
    icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    color: '#6b7280'
  }
}

/**
 * Determine category from property URL
 * Analyzes URL patterns to automatically categorize properties
 * 
 * @param {string} url - The property URL to analyze
 * @returns {string} Category key (e.g., 'venta-casas', 'alquiler-apartamentos')
 */
export const getCategoryFromUrl = (url: string): string => {
  if (!url) return 'other'
  const urlLower = url.toLowerCase()
  
  // Encuentra24 patterns
  if (urlLower.includes('proyectos-nuevos')) return 'nuevos-proyectos'
  if (urlLower.includes('venta-de-propiedades-casas') || urlLower.includes('venta-casas')) return 'venta-casas'
  if (urlLower.includes('venta-de-propiedades-apartamentos') || urlLower.includes('venta-apartamentos')) return 'venta-apartamentos'
  if (urlLower.includes('venta-de-propiedades-negocios')) return 'venta-negocios'
  if (urlLower.includes('venta-de-propiedades-lotes-y-terrenos') || urlLower.includes('lotes')) return 'venta-lotes'
  if (urlLower.includes('venta-de-propiedades-fincas')) return 'venta-fincas'
  if (urlLower.includes('alquiler-casas')) return 'alquiler-casas'
  if (urlLower.includes('alquiler-apartamentos')) return 'alquiler-apartamentos'
  if (urlLower.includes('alquiler-locales-comerciales')) return 'alquiler-locales'
  
  // Coldwell Banker patterns
  if (urlLower.includes('coldwellbanker')) {
    if (urlLower.includes('house-for-sale') || urlLower.includes('casa-en-venta')) return 'venta-casas'
    if (urlLower.includes('apartment-for-sale') || urlLower.includes('apartamento-en-venta')) return 'venta-apartamentos'
    if (urlLower.includes('land-for-sale') || urlLower.includes('terreno-en-venta') || urlLower.includes('lote-en-venta')) return 'venta-lotes'
    if (urlLower.includes('farm-for-sale') || urlLower.includes('finca-en-venta')) return 'venta-fincas'
    if (urlLower.includes('commercial-for-sale') || urlLower.includes('comercial-en-venta')) return 'venta-negocios'
    if (urlLower.includes('house-for-rent') || urlLower.includes('casa-alquiler')) return 'alquiler-casas'
    if (urlLower.includes('apartment-for-rent') || urlLower.includes('apartamento-alquiler')) return 'alquiler-apartamentos'
    if (urlLower.includes('commercial-for-rent') || urlLower.includes('local-alquiler')) return 'alquiler-locales'
    return 'venta-casas'
  }
  
  return 'other'
}
