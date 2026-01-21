"""
Restaurant content type module.

NOTE: Restaurant prompts are now in content_types/prompts.py (centralized)
"""

from .config import RestaurantConfig
from .schema import (
    RESTAURANT_FIELD_MAPPING,
    RESTAURANT_SPECIFIC_SCHEMA,
)

__all__ = [
    'RestaurantConfig',
    'RESTAURANT_FIELD_MAPPING',
    'RESTAURANT_SPECIFIC_SCHEMA',
]
