/**
 * Formatters
 * 
 * Utility functions for formatting data (prices, dates, numbers, etc.)
 */

/**
 * Format price value for display
 * 
 * @param {number | undefined | null} price - Price value to format
 * @returns {string} Formatted price string (e.g., "350,000" or "N/A")
 */
export const formatPrice = (price: number | undefined | null): string => {
  if (price === undefined || price === null) return 'N/A'
  
  return price.toLocaleString('en-US', { 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  })
}

/**
 * Format date string for display
 * 
 * @param {string | undefined} dateString - ISO date string
 * @returns {string} Formatted date (e.g., "15 ene, 10:30" or "N/A")
 */
export const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'N/A'
  
  return new Date(dateString).toLocaleString('es-ES', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Format time ago (relative time)
 * 
 * @param {string} dateString - ISO date string
 * @returns {string} Relative time string (e.g., "hace 5 min", "hace 2h", "hace 3d")
 */
export const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'hace un momento'
  if (minutes < 60) return `hace ${minutes} min`
  if (hours < 24) return `hace ${hours}h`
  if (days < 30) return `hace ${days}d`
  
  return formatDate(dateString)
}

/**
 * Format number with units
 * 
 * @param {number | undefined | null} value - Numeric value
 * @param {string} unit - Unit string (e.g., 'm²', 'km', 'años')
 * @returns {string} Formatted string (e.g., "150 m²" or "N/A")
 */
export const formatWithUnit = (
  value: number | undefined | null,
  unit: string
): string => {
  if (value === undefined || value === null) return 'N/A'
  return `${value.toLocaleString('en-US')} ${unit}`
}

/**
 * Format percentage
 * 
 * @param {number} value - Percentage value (0-1 or 0-100)
 * @param {boolean} isDecimal - Whether value is in decimal format (0-1)
 * @returns {string} Formatted percentage (e.g., "85%")
 */
export const formatPercentage = (value: number, isDecimal: boolean = true): string => {
  const percentage = isDecimal ? value * 100 : value
  return `${Math.round(percentage)}%`
}

/**
 * Truncate text to specified length
 * 
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * Format array as comma-separated string
 * 
 * @param {string[] | undefined} items - Array of strings
 * @param {string} fallback - Fallback value if array is empty
 * @returns {string} Comma-separated string or fallback
 */
export const formatList = (items: string[] | undefined, fallback: string = 'N/A'): string => {
  if (!items || items.length === 0) return fallback
  return items.join(', ')
}

/**
 * Format area with unit
 * 
 * @param {number} area - Area value
 * @param {string} unit - Unit of measurement
 * @returns {string} Formatted area with unit
 */
export const formatArea = (area: number, unit: string = 'm²'): string => {
  return `${area.toLocaleString()} ${unit}`;
}

/**
 * Format boolean value
 * 
 * @param {boolean | undefined} value - Boolean value
 * @returns {string} Formatted boolean
 */
export const formatBoolean = (value: boolean | undefined): string => {
  if (value === undefined || value === null) return 'N/A';
  return value ? 'Sí' : 'No';
}

