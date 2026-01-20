/**
 * PropertyData Interface
 * 
 * Main interface for property data extracted from various sources.
 * Supports multiple content types: real_estate, tour, restaurant, transportation, local_tips
 */
export interface PropertyData {
  // Core fields
  id?: string
  property_name?: string
  listing_id?: string
  listing_status?: string
  price_usd?: number
  
  // Price details (nested object for different pricing structures)
  price_details?: {
    // General pricing
    display_price?: string
    sale_price?: number
    rental_price?: number
    currency?: string
    adults?: number
    children?: number
    students?: number
    nationals?: number
    seniors?: number
    groups?: number
    range?: string
    note?: string
    
    // Restaurant pricing
    average_price?: number
    price_level?: string
    appetizers_range?: string
    mains_range?: string
    desserts_range?: string
    drinks_range?: string
    
    // Hotel pricing
    low_season?: number
    high_season?: number
    standard_room?: number
    deluxe_room?: number
    suite?: number
    
    // Transportation pricing
    one_way?: number
    one_way_price?: number
    round_trip?: number
    round_trip_price?: number
    per_person?: number
    per_vehicle?: number
    discounts?: string[]
    
    // Tour pricing
    adult_price?: number
    child_price?: number
    group_price?: number
  }
  
  // Property details
  property_type?: string
  property_type_display?: string
  location?: string | {
    address?: string
    city?: string
    state?: string
    country?: string
    postal_code?: string
    coordinates?: {
      lat: number
      lng: number
    }
  }
  latitude?: number
  longitude?: number
  bedrooms?: number
  bathrooms?: number
  square_meters?: number
  lot_size_m2?: number
  date_listed?: string
  status?: string
  status_display?: string
  description?: string
  
  // Additional structured fields
  details?: {
    property_type?: string
    bedrooms?: number
    bathrooms?: number
    area?: number
    area_unit?: string
    lot_size?: number
    lot_size_unit?: string
    year_built?: number
    furnished?: boolean
    parking_spaces?: number
    floors?: number
    hoa_fee?: number
  }
  
  // Contact information
  contact?: {
    name?: string
    email?: string
    phone?: string
    whatsapp?: string
  }
  
  // Content arrays
  images?: string[]
  features?: string[]
  
  // Content type specific
  content_type?: string
  category?: string
  cuisine_type?: string
  transport_type?: string
  tip_type?: string
  
  // Tour fields
  tour_schedule?: any
  inclusions?: string[]
  exclusions?: string[]
  requirements?: string[]
  
  // Restaurant fields
  operating_hours?: Record<string, string>
  menu_items?: any[]
  
  // Transportation fields
  routes?: any[]
  schedule?: any
  vehicle_info?: any
  booking_info?: any
  
  // Local tips fields
  tips_by_category?: Record<string, string[]>
  key_points?: string[]
  dos?: string[]
  donts?: string[]
  best_time?: any
  useful_links?: any[]
  additional_tips?: string[]
  
  // Metadata
  timestamp?: string
  processed_by?: string
  
  // Source information
  source_url?: string
  source_website?: string
  created_at?: string
  extraction_confidence?: number
  
  // Content type specific fields (dynamic)
  // Allow any additional fields for flexibility across content types
  [key: string]: any
}
