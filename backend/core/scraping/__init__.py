"""
Core scraping module.

This module provides tools for scraping property data from real estate websites.

Key components:
- WebScraper: Main scraper class using Scrapfly
- Extractors: Site-specific extraction rules for different websites (TODO: migrate)
- get_extractor(): Auto-detect and return appropriate extractor for a URL (TODO: migrate)

Usage:
    from core.scraping import WebScraper, scrape_url
    
    # Scrape a URL
    result = scrape_url(url)
"""

from .scraper import WebScraper, scrape_url, ScraperError
# from .extractors import get_extractor, EXTRACTORS, BaseExtractor  # TODO: extractors.py missing

__all__ = [
    'WebScraper',
    'scrape_url',
    'ScraperError',
]

