"""
Extraction module for web scraping and data extraction.
Contains content detection, page type detection, and web search enrichment.
"""

from .extractor import PropertyExtractor, ExtractionError, extract_content_data, extract_property_data
from .content_detection import detect_content_type
from .page_type_detection import PageTypeDetector, detect_page_type
from .web_search import WebSearchService, get_web_search_service

__all__ = [
    'PropertyExtractor',
    'ExtractionError',
    'extract_content_data',
    'extract_property_data',
    'detect_content_type',
    'PageTypeDetector',
    'detect_page_type',
    'WebSearchService',
    'get_web_search_service',
]
