/**
 * Validators
 * 
 * Validation utilities for user input and data
 */

/**
 * Validate URL format
 * 
 * @param {string} url - URL string to validate
 * @returns {boolean} True if valid URL, false otherwise
 */
export const validateUrl = (url: string): boolean => {
  if (!url || url.trim().length === 0) return false
  
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Validate text input (non-empty)
 * 
 * @param {string} text - Text string to validate
 * @returns {boolean} True if non-empty text, false otherwise
 */
export const validateText = (text: string): boolean => {
  return Boolean(text && text.trim().length > 0);
}

/**
 * Get confidence level classification
 * 
 * @param {number} confidence - Confidence value (0-1)
 * @returns {object} Object with label and colorClass
 */
export const getConfidenceLevel = (confidence: number): {
  label: string
  colorClass: string
} => {
  if (confidence >= 0.8) {
    return { 
      label: 'Alta', 
      colorClass: 'bg-green-100 text-green-800' 
    }
  } else if (confidence >= 0.6) {
    return { 
      label: 'Media', 
      colorClass: 'bg-yellow-100 text-yellow-800' 
    }
  } else {
    return { 
      label: 'Baja', 
      colorClass: 'bg-red-100 text-red-800' 
    }
  }
}

/**
 * Validate email format
 * 
 * @param {string} email - Email string to validate
 * @returns {boolean} True if valid email, false otherwise
 */
export const validateEmail = (email: string): boolean => {
  if (!email) return false
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (basic international format)
 * 
 * @param {string} phone - Phone number to validate
 * @returns {boolean} True if valid phone, false otherwise
 */
export const validatePhone = (phone: string): boolean => {
  if (!phone) return false
  
  // Remove spaces, dashes, parentheses
  const cleaned = phone.replace(/[\s\-()]/g, '')
  
  // Check if it's numeric and has reasonable length
  const phoneRegex = /^[\+]?[0-9]{7,15}$/
  return phoneRegex.test(cleaned)
}

/**
 * Validate number in range
 * 
 * @param {number} value - Number to validate
 * @param {number} min - Minimum value (inclusive)
 * @param {number} max - Maximum value (inclusive)
 * @returns {boolean} True if in range, false otherwise
 */
export const validateRange = (
  value: number, 
  min: number, 
  max: number
): boolean => {
  return value >= min && value <= max
}

/**
 * Check if value is a valid positive number
 * 
 * @param {any} value - Value to check
 * @returns {boolean} True if positive number, false otherwise
 */
export const isPositiveNumber = (value: any): boolean => {
  return typeof value === 'number' && !isNaN(value) && value > 0
}

/**
 * Sanitize text input (remove potentially harmful characters)
 * 
 * @param {string} text - Text to sanitize
 * @returns {string} Sanitized text
 */
export const sanitizeText = (text: string): string => {
  if (!text) return ''
  
  // Remove HTML tags
  return text.replace(/<[^>]*>/g, '')
}
