"""
Schema definition for Real Estate content type.
"""

from typing import Optional, List
from decimal import Decimal


# Field mappings: No mapping needed, already uses property_name
REAL_ESTATE_FIELD_MAPPING = {}


# Schema for specific property
REAL_ESTATE_SPECIFIC_SCHEMA = {
    'property_name': str,
    'property_type': Optional[str],
    'price_usd': Optional[Decimal],
    'location': Optional[str],
    'city': Optional[str],
    'province': Optional[str],
    'country': Optional[str],
    'listing_type': Optional[str],  # sale, rent
    'bedrooms': Optional[int],
    'bathrooms': Optional[float],
    'area_m2': Optional[float],
    'lot_size_m2': Optional[float],
    'parking_spaces': Optional[int],
    'description': Optional[str],
    'amenities': Optional[List[str]],
    'date_listed': Optional[str],
    'status': Optional[str],
    'extraction_confidence': float,
}
