/**
 * API Configuration
 * 
 * Centralizes API base URL configuration and environment handling
 */

/**
 * Get the API base URL from environment variables
 * Handles trailing slashes and /api suffix removal for DigitalOcean deployments
 * 
 * @returns {string} The configured API base URL
 */
export const getApiBase = (): string => {
  let baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  
  console.log('🔧 [API CONFIG] Raw VITE_API_URL:', import.meta.env.VITE_API_URL)
  console.log('🔧 [API CONFIG] Initial baseUrl:', baseUrl)
  
  // Remover trailing slash si existe
  if (baseUrl.endsWith('/')) {
    baseUrl = baseUrl.slice(0, -1)
  }
  
  // Remover /api si ya viene incluido en VITE_API_URL (DigitalOcean lo agrega automáticamente)
  if (baseUrl.endsWith('/api')) {
    baseUrl = baseUrl.slice(0, -4)
    console.log('🔧 [API CONFIG] Removed /api suffix, new baseUrl:', baseUrl)
  }
  
  console.log('✅ [API CONFIG] Final API_BASE:', baseUrl)
  return baseUrl
}

/**
 * Configured API base URL for all requests
 * Use this constant throughout the application
 */
export const API_BASE = getApiBase()

console.log('🌐 [API CONFIG] API_BASE será usado en todas las requests:', API_BASE)
