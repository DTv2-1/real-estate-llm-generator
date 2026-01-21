"""
Content Types Registry - New modular structure.

This module provides a centralized registry for all content types and their configurations.
Each content type (tour, restaurant, real_estate, etc.) has its own subdirectory with:
  - prompts.py: Extraction prompts (specific and general)
  - config.py: Configuration (domains, keywords, critical fields)
  - schema.py: Data schemas and field mappings

Usage:
    from core.llm.content_types import get_content_type_config, get_extraction_prompt
    
    config = get_content_type_config('tour')
    prompt = get_extraction_prompt('tour', page_type='specific')
"""

from typing import Dict, List, Any

from .base import ContentTypeConfig, PAGE_TYPE_SPECIFIC, PAGE_TYPE_GENERAL
from .tour import TourConfig
from .restaurant import RestaurantConfig
from .real_estate import RealEstateConfig
from .transportation.config import TransportationConfig
from .local_tips.config import LocalTipsConfig
from .prompts import (
    TOUR_SPECIFIC_PROMPT,
    TOUR_GENERAL_PROMPT,
    RESTAURANT_SPECIFIC_PROMPT,
    RESTAURANT_GENERAL_PROMPT,
    PROPERTY_EXTRACTION_PROMPT,
    get_extraction_prompt as _get_prompt_helper,
)


# ============================================================================
# CONTENT TYPE REGISTRY
# ============================================================================

# Registry of all content type configurations
CONTENT_TYPE_REGISTRY: Dict[str, ContentTypeConfig] = {
    'real_estate': RealEstateConfig,
    'tour': TourConfig,
    'restaurant': RestaurantConfig,
    'transportation': TransportationConfig,
    'local_tips': LocalTipsConfig,
}


# Legacy CONTENT_TYPES dict for backward compatibility
CONTENT_TYPES: Dict[str, Dict[str, Any]] = {
    key: config.to_dict()
    for key, config in CONTENT_TYPE_REGISTRY.items()
}


# ============================================================================
# PROMPT REGISTRY
# ============================================================================

# Map: (content_type, page_type) → prompt
PROMPT_REGISTRY = {
    ('tour', 'specific'): TOUR_SPECIFIC_PROMPT,
    ('tour', 'general'): TOUR_GENERAL_PROMPT,
    ('restaurant', 'specific'): RESTAURANT_SPECIFIC_PROMPT,
    ('restaurant', 'general'): RESTAURANT_GENERAL_PROMPT,
    ('real_estate', 'specific'): PROPERTY_EXTRACTION_PROMPT,
    # Transportation and local_tips prompts in legacy content_types.py (to migrate)
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_content_type_config(content_type: str) -> ContentTypeConfig:
    """
    Get configuration for a specific content type.
    
    Args:
        content_type: Type key (tour, restaurant, real_estate, etc.)
        
    Returns:
        ContentTypeConfig class
        
    Raises:
        ValueError: If content type not found
    """
    if content_type not in CONTENT_TYPE_REGISTRY:
        available = ', '.join(CONTENT_TYPE_REGISTRY.keys())
        raise ValueError(f"Unknown content type: {content_type}. Available: {available}")
    
    return CONTENT_TYPE_REGISTRY[content_type]


def get_extraction_prompt(content_type: str, page_type: str = 'specific') -> str:
    """
    Get the extraction prompt for a content type and page type.
    
    Args:
        content_type: Type of content (tour, restaurant, real_estate, etc.)
        page_type: 'specific' (single item) or 'general' (guide/listing)
        
    Returns:
        Appropriate extraction prompt string
    """
    # Use the centralized prompts module
    from .prompts import get_extraction_prompt as _get_prompt
    
    # Convert page_type to is_specific boolean
    is_specific = (page_type == 'specific')
    
    return _get_prompt(content_type, is_specific=is_specific)


def get_all_content_types() -> List[Dict[str, str]]:
    """
    Get list of all content types for UI display.
    
    Returns:
        List of dicts with keys: key, label, icon, description
    """
    return [
        config.to_dict()
        for config in CONTENT_TYPE_REGISTRY.values()
    ]


def get_critical_fields(content_type: str) -> List[str]:
    """
    Get list of critical fields for a content type.
    These are fields that should trigger web search if missing.
    
    Args:
        content_type: Type key
        
    Returns:
        List of critical field names
    """
    config = get_content_type_config(content_type)
    return config.CRITICAL_FIELDS


def get_allowed_fields(content_type: str) -> List[str]:
    """
    Get list of allowed fields for validation.
    
    Args:
        content_type: Type key
        
    Returns:
        List of allowed field names
    """
    config = get_content_type_config(content_type)
    return config.ALLOWED_FIELDS


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main functions
    'get_content_type_config',
    'get_extraction_prompt',
    'get_all_content_types',
    'get_critical_fields',
    'get_allowed_fields',
    
    # Legacy compatibility
    'CONTENT_TYPES',
    
    # Constants
    'PAGE_TYPE_SPECIFIC',
    'PAGE_TYPE_GENERAL',
    
    # Prompts (for direct import if needed)
    'TOUR_SPECIFIC_PROMPT',
    'TOUR_GENERAL_PROMPT',
    'RESTAURANT_SPECIFIC_PROMPT',
    'RESTAURANT_GENERAL_PROMPT',
    'PROPERTY_EXTRACTION_PROMPT',
    
    # Registries
    'CONTENT_TYPE_REGISTRY',
    'PROMPT_REGISTRY',
    
    # Config classes
    'TourConfig',
    'RestaurantConfig',
    'RealEstateConfig',
    'TransportationConfig',
    'LocalTipsConfig',
]
