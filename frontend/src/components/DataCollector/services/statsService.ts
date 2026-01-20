/**
 * Stats Service
 * 
 * Handles statistics and configuration endpoints
 */

import { API_BASE } from './apiConfig'
import type { ContentType, WebsiteConfig } from '../types'

/**
 * Load ingestion statistics
 * Returns daily processing count and recent properties
 * 
 * @returns {Promise<any>} Stats data with properties_today and recent_properties
 */
export const loadIngestionStats = async () => {
  const url = `${API_BASE}/ingest/stats/`
  console.log('📥 [FETCH] Loading ingestion stats from:', url)
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const data = await response.json()
  console.log('📥 [FETCH] Stats received:', data)
  
  return data
}

/**
 * Load available content types from backend
 * Returns list of content types (tour, restaurant, transportation, etc.)
 * 
 * @returns {Promise<ContentType[]>} Array of content types
 */
export const loadContentTypes = async (): Promise<ContentType[]> => {
  const url = `${API_BASE}/ingest/content-types/`
  console.log('📥 [FETCH] Loading content types from:', url)
  
  const response = await fetch(url)
  const data = await response.json()
  
  if (data.status === 'success') {
    console.log('✅ Content types loaded:', data.content_types.length)
    return data.content_types
  }
  
  return []
}

/**
 * Load supported websites configuration
 * Returns list of websites with extractors available
 * 
 * @returns {Promise<WebsiteConfig[]>} Array of website configurations
 */
export const loadSupportedWebsites = async (): Promise<WebsiteConfig[]> => {
  const url = `${API_BASE}/ingest/supported-websites/`
  console.log('📥 [FETCH] Loading supported websites from:', url)
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const data = await response.json()
  console.log('📥 [FETCH] Supported websites:', data.websites)
  
  return data.websites
}
