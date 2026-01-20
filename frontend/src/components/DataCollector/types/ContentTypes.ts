/**
 * Content Type Interfaces
 * 
 * Interfaces for managing different content types in the system
 * (real_estate, tour, restaurant, transportation, local_tips)
 */

/**
 * ContentType Interface
 * Represents a content type available in the system
 */
export interface ContentType {
  id: string           // Unique identifier (e.g., 'tour', 'restaurant')
  key: string          // Unique identifier (e.g., 'tour', 'restaurant')
  name: string         // Display name (e.g., 'Tour / Actividad')
  label: string        // Display name (e.g., '🎫 Tour / Actividad')
  icon: string         // Emoji or icon string
  description: string  // Description text for the content type
}

/**
 * CategoryConfig Interface
 * Configuration for real estate categories (legacy support)
 */
export interface CategoryConfig {
  id: string     // Unique identifier (e.g., 'venta-casas')
  name: string   // Display name (e.g., 'Casas en Venta')
  icon: string   // SVG icon as string
  color: string  // Hex color code (e.g., '#10b981')
}
