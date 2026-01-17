from typing import TypedDict, List, Optional, Any
from decimal import Decimal

class PropertyData(TypedDict, total=False):
    """Standardized property data structure."""
    title: Optional[str]
    price_usd: Optional[Decimal]
    bedrooms: Optional[int]
    bathrooms: Optional[Decimal]
    area_m2: Optional[Decimal]
    lot_size_m2: Optional[Decimal]
    description: Optional[str]
    property_type: Optional[str]
    listing_type: Optional[str]
    location: Optional[str]
    address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    images: List[str]
    amenities: List[str]
    agent_name: Optional[str]
    agent_phone: Optional[str]
    agent_email: Optional[str]
    year_built: Optional[int]
    parking_spaces: Optional[int]
    source_url: Optional[str]
    source_website: str
    
    # Custom/Optional fields that might be extracted
    # We use total=False so these are optional, but typed if present
    construction_stage: Optional[str]
    listing_id: Optional[str]
    date_listed: Optional[str]
    pool: Optional[bool]
    floor: Optional[str]
    hoa_fee: Optional[Decimal]
    taxes: Optional[Decimal]
    video_url: Optional[str]
    brochure_url: Optional[str]
    zoning: Optional[str]
    price_text: Optional[str] # Original price text if needed
    price_per_sqm: Optional[str] # Original price per sqm text
