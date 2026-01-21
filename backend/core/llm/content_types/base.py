"""
Base configuration and utilities for content types.
Shared constants and base classes for all content type modules.
"""

from typing import Dict, List, Any


class ContentTypeConfig:
    """Base configuration class for content types."""
    
    # Override these in subclasses
    KEY = 'base'
    LABEL = 'Base Content Type'
    ICON = '📄'
    DESCRIPTION = 'Base content type'
    
    # Domains that typically have this content type
    DOMAINS: List[str] = []
    
    # Keywords that indicate this content type
    KEYWORDS: List[str] = []
    
    # Fields that are critical and should trigger web search if missing
    CRITICAL_FIELDS: List[str] = []
    
    # Fields allowed in validation (whitelist)
    ALLOWED_FIELDS: List[str] = []
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'key': cls.KEY,
            'label': cls.LABEL,
            'icon': cls.ICON,
            'description': cls.DESCRIPTION,
            'domains': cls.DOMAINS,
            'keywords': cls.KEYWORDS,
        }


# Generic fields present in all content types
GENERIC_FIELDS = [
    'property_name',      # Generic name field (maps to tour_name, restaurant_name, etc.)
    'property_type',      # Generic type field
    'location',           # Geographic location
    'description',        # Long-form description
    'price_usd',          # Base price in USD
    'source_url',         # Original URL
    'source_website',     # Source domain
    'extraction_confidence',  # LLM confidence score
]


# Page types
PAGE_TYPE_SPECIFIC = 'specific'   # Single item (e.g., specific tour, specific property)
PAGE_TYPE_GENERAL = 'general'     # Guide/listing (e.g., "Top 10 tours in Costa Rica")
