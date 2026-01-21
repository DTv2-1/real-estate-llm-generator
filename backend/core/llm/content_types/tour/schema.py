"""
Schema definition for Tour content type.
Defines the structure and fields for tour data.
"""

from typing import Dict, List, Optional, Any
from decimal import Decimal


# Field mappings: tour-specific → generic Property model
TOUR_FIELD_MAPPING = {
    'tour_name': 'property_name',
    'tour_type': 'property_type',
}


# Schema for specific tour
TOUR_SPECIFIC_SCHEMA = {
    'tour_name': str,
    'tour_type': str,  # adventure, cultural, wildlife, beach, food, sightseeing, water_sports, other
    'price_usd': Optional[Decimal],
    'price_details': Optional[Dict],
    'duration_hours': Optional[float],
    'difficulty_level': Optional[str],  # easy, moderate, challenging, extreme
    'location': Optional[str],
    'description': Optional[str],
    'included_items': Optional[List[str]],
    'excluded_items': Optional[List[str]],
    'max_participants': Optional[int],
    'languages_available': Optional[List[str]],
    'pickup_included': Optional[bool],
    'minimum_age': Optional[int],
    'cancellation_policy': Optional[str],
    'extraction_confidence': float,
}


# Schema for general tour guide
TOUR_GENERAL_SCHEMA = {
    'page_type': str,  # 'general_guide'
    'destination': Optional[str],
    'overview': Optional[str],
    'tour_types_available': Optional[List[str]],
    'regions': Optional[List[Dict]],
    'price_range': Optional[Dict],
    'best_season': Optional[str],
    'seasonal_activities': Optional[List[Dict]],
    'best_time_of_day': Optional[str],
    'duration_range': Optional[str],
    'tips': Optional[List[str]],
    'things_to_bring': Optional[List[str]],
    'featured_tours': Optional[List[Dict]],
    'total_tours_mentioned': Optional[int],
    'booking_tips': Optional[str],
    'faqs': Optional[List[Dict]],
    'what_to_pack': Optional[List[str]],
    'family_friendly': Optional[bool],
    'accessibility_info': Optional[str],
    'extraction_confidence': float,
}
