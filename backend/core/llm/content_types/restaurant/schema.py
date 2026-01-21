"""
Schema definition for Restaurant content type.
"""

from typing import Dict, List, Optional
from decimal import Decimal


# Field mappings: restaurant-specific → generic Property model
RESTAURANT_FIELD_MAPPING = {
    'restaurant_name': 'property_name',
    'cuisine_type': 'property_type',
}


# Schema for specific restaurant
RESTAURANT_SPECIFIC_SCHEMA = {
    'restaurant_name': str,
    'cuisine_type': Optional[str],
    'price_range': Optional[str],  # budget, moderate, upscale, fine_dining
    'average_price_per_person': Optional[Decimal],
    'price_details': Optional[Dict],
    'location': Optional[str],
    'description': Optional[str],
    'signature_dishes': Optional[List[str]],
    'atmosphere': Optional[str],
    'opening_hours': Optional[Dict],
    'reservation_required': Optional[bool],
    'dietary_options': Optional[List[str]],
    'amenities': Optional[List[str]],
    'special_experiences': Optional[str],
    'dress_code': Optional[str],
    'contact_phone': Optional[str],
    'rating': Optional[float],
    'number_of_reviews': Optional[int],
    'parking_available': Optional[bool],
    'extraction_confidence': float,
}
