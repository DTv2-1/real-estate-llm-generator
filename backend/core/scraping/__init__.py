"""
Core scraping module.

This module provides tools for scraping property data from real estate websites.

Key components:
- WebScraper: Main scraper class using Scrapfly
- Extractors: Site-specific extraction rules for different websites
- get_extractor(): Auto-detect and return appropriate extractor for a URL

Usage:
    from core.scraping import WebScraper, get_extractor
    
    # Scrape a URL
    scraper = WebScraper()
    result = scraper.scrape(url)
    
    # Extract property data
    extractor = get_extractor(url)
    property_data = extractor.extract(result['html'])
"""

from .scraper import WebScraper, scrape_url, ScraperError
from .extractors import get_extractor, EXTRACTORS, BaseExtractor

__all__ = [
    'WebScraper',
    'scrape_url',
    'ScraperError',
    'get_extractor',
    'EXTRACTORS',
    'BaseExtractor',
]
