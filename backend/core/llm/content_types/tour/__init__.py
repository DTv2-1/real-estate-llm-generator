"""
Tour content type module.

NOTE: Tour prompts are now in content_types/prompts.py (centralized)
"""

from .config import TourConfig
from .schema import (
    TOUR_FIELD_MAPPING,
    TOUR_SPECIFIC_SCHEMA,
    TOUR_GENERAL_SCHEMA,
)

__all__ = [
    'TourConfig',
    'TOUR_FIELD_MAPPING',
    'TOUR_SPECIFIC_SCHEMA',
    'TOUR_GENERAL_SCHEMA',
]
