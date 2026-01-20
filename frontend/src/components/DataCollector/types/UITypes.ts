/**
 * UI-Related Type Interfaces
 * 
 * Interfaces for UI components and recent property displays
 */

/**
 * RecentProperty Interface
 * Represents a recently processed property in the dashboard
 */
export interface RecentProperty {
  id: string
  title: string
  location: string
  price_usd: number | null
  bedrooms: number | null
  bathrooms: number | null
  source_website: string
  created_at: string
}

/**
 * WebsiteConfig Interface
 * Configuration for supported websites/extractors
 */
export interface WebsiteConfig {
  id: string
  name: string
  url: string | null
  color: string
  active: boolean
  has_extractor: boolean
}
