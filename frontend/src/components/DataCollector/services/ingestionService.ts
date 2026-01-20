/**
 * Ingestion Service
 * 
 * Handles property extraction and processing operations
 */

import { API_BASE } from './apiConfig'

/**
 * Process property from URL or text input
 * Starts the extraction job and returns task_id for WebSocket tracking
 * 
 * @param {('url' | 'text')} inputType - Type of input (url or text)
 * @param {string} value - The URL or text content to process
 * @param {string} selectedContentType - The content type to use ('auto' for auto-detection)
 * @returns {Promise<any>} Processing response with task_id or property data
 */
export const processProperty = async (
  inputType: 'url' | 'text',
  value: string,
  selectedContentType: string
) => {
  const endpoint = inputType === 'url' 
    ? `${API_BASE}/ingest/url/` 
    : `${API_BASE}/ingest/text/`
  
  console.log('📤 [FETCH] Starting processing job:', endpoint)
  
  // Si es 'auto', enviamos null para que el backend detecte automáticamente
  const contentTypeValue = selectedContentType === 'auto' ? null : selectedContentType
  
  const body = inputType === 'url' 
    ? { url: value, content_type: contentTypeValue, use_websocket: true }
    : { text: value, content_type: contentTypeValue, use_websocket: true }
  
  console.log('📤 [FETCH] Request body:', body)

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body)
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}
