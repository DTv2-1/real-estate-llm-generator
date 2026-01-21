"""
Real Estate content type module.
Note: Uses PROPERTY_EXTRACTION_PROMPT from prompts.py for backward compatibility.
"""

# Real estate prompts are imported from the legacy prompts.py file
# This maintains backward compatibility with existing code

from .config import RealEstateConfig
from .schema import REAL_ESTATE_FIELD_MAPPING, REAL_ESTATE_SPECIFIC_SCHEMA

__all__ = [
    'RealEstateConfig',
    'REAL_ESTATE_FIELD_MAPPING',
    'REAL_ESTATE_SPECIFIC_SCHEMA',
]
