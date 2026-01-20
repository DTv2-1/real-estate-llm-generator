/**
 * Property Service
 * 
 * Handles all property-related API operations (CRUD)
 */

import { API_BASE } from './apiConfig'
import type { PropertyData } from '../types'

/**
 * Load property history from backend
 * Fetches the 100 most recent properties ordered by creation date
 * 
 * @returns {Promise<PropertyData[]>} Array of property data
 */
export const loadHistoryFromBackend = async (): Promise<PropertyData[]> => {
  const url = `${API_BASE}/properties/?page_size=100&ordering=-created_at`
  console.log('📥 [FETCH] Loading history from:', url)
  
  const response = await fetch(url)
  console.log('📥 [FETCH] Response status:', response.status, response.ok ? '✅' : '❌')
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const data = await response.json()
  console.log('📥 [FETCH] Data received:', data.results?.length || 0, 'properties')
  
  return data.results || []
}

/**
 * Load a single property by ID from history
 * 
 * @param {string} propertyId - The property ID to load
 * @returns {Promise<PropertyData>} Property data
 */
export const loadPropertyFromHistory = async (propertyId: string): Promise<PropertyData> => {
  const response = await fetch(`${API_BASE}/properties/${propertyId}/`)
  
  if (!response.ok) {
    throw new Error(`Failed to load property: ${response.status}`)
  }
  
  return await response.json()
}

/**
 * Save property data to the database
 * 
 * @param {PropertyData} propertyData - The property data to save
 * @returns {Promise<{response: Response, data: any}>} Response and parsed data
 */
export const saveProperty = async (propertyData: PropertyData) => {
  const response = await fetch(`${API_BASE}/ingest/save/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ property_data: propertyData })
  })

  const data = await response.json()
  
  console.log('Save response status:', response.status)
  console.log('Save response data:', data)
  
  return { response, data }
}

/**
 * Clear all properties from history
 * Deletes all properties from the database
 * 
 * @returns {Promise<boolean>} Success status
 */
export const clearHistory = async (): Promise<boolean> => {
  const response = await fetch(`${API_BASE}/properties/?page_size=100`)
  const data = await response.json()
  
  // Delete each property individually
  for (const prop of data.results) {
    await fetch(`${API_BASE}/properties/${prop.id}/`, { method: 'DELETE' })
  }
  
  return true
}
