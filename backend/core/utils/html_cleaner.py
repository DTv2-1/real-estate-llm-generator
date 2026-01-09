"""
HTML Cleaner Utility
Reduces HTML size by extracting only relevant content for property extraction.
Optimizes token usage for OpenAI API calls.
"""

from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional


class HTMLCleaner:
    """
    Clean and optimize HTML for property data extraction.
    Removes unnecessary elements and keeps only relevant content.
    """
    
    # Elements to remove (scripts, styles, etc.)
    REMOVE_TAGS = [
        'script', 'style', 'link', 'meta', 'noscript', 
        'iframe', 'svg', 'path', 'g', 'defs',
        'header', 'footer', 'nav', 'aside'
    ]
    
    # Classes/IDs that typically contain forms, ads, etc.
    REMOVE_PATTERNS = [
        r'cookie', r'gdpr', r'popup', r'modal', r'advertisement',
        r'social-share', r'newsletter', r'subscribe', r'footer',
        r'header', r'navigation', r'menu', r'sidebar',
        r'recaptcha', r'captcha', r'tracking', r'analytics'
    ]
    
    def __init__(self, html: str):
        """Initialize with HTML string."""
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        
    def clean(self) -> str:
        """
        Main cleaning method. Returns optimized HTML.
        Reduces size by 70-90% typically.
        """
        # Remove unnecessary tags
        self._remove_tags()
        
        # Remove elements by class/id patterns
        self._remove_by_patterns()
        
        # Remove inline styles and unnecessary attributes
        self._clean_attributes()
        
        # Remove empty elements
        self._remove_empty_elements()
        
        # Get cleaned HTML
        cleaned_html = str(self.soup)
        
        # Additional text cleaning
        cleaned_html = self._clean_text(cleaned_html)
        
        return cleaned_html
    
    def _remove_tags(self):
        """Remove script, style, and other unnecessary tags."""
        for tag_name in self.REMOVE_TAGS:
            for tag in self.soup.find_all(tag_name):
                tag.decompose()
    
    def _remove_by_patterns(self):
        """Remove elements matching common non-content patterns."""
        # Get all elements first (avoid modification during iteration)
        elements = list(self.soup.find_all(True))
        
        for element in elements:
            # Skip if element has been decomposed
            if not element or not element.parent:
                continue
                
            # Check class attribute
            try:
                classes = element.get('class', [])
                class_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
            except (AttributeError, TypeError):
                class_str = ''
            
            # Check id attribute
            try:
                elem_id = element.get('id', '')
            except (AttributeError, TypeError):
                elem_id = ''
            
            # Combine for pattern matching
            combined = f"{class_str} {elem_id}".lower()
            
            # Remove if matches any pattern
            for pattern in self.REMOVE_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    try:
                        element.decompose()
                    except:
                        pass
                    break
    
    def _clean_attributes(self):
        """Remove inline styles and keep only essential attributes."""
        # Attributes to keep
        KEEP_ATTRS = ['class', 'id', 'href', 'src', 'alt', 'title']
        
        for tag in self.soup.find_all(True):
            if not tag or not tag.parent:
                continue
                
            try:
                # Get current attributes
                attrs = dict(tag.attrs)
                
                # Remove unwanted attributes
                for attr in list(attrs.keys()):
                    if attr not in KEEP_ATTRS:
                        try:
                            del tag.attrs[attr]
                        except (KeyError, AttributeError):
                            pass
            except (AttributeError, TypeError):
                continue
    
    def _remove_empty_elements(self):
        """Remove elements with no content or only whitespace."""
        for element in self.soup.find_all(True):
            # Skip certain elements that can be empty
            if element.name in ['br', 'hr', 'img', 'input']:
                continue
                
            # Check if element is empty
            if not element.get_text(strip=True) and not element.find_all('img'):
                element.decompose()
    
    def _clean_text(self, html: str) -> str:
        """Clean up whitespace and formatting in HTML string."""
        # Remove excessive whitespace
        html = re.sub(r'\s+', ' ', html)
        
        # Remove whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        
        return html.strip()
    
    def get_size_reduction(self) -> Dict[str, int]:
        """Return size statistics before and after cleaning."""
        cleaned = self.clean()
        original_size = len(self.html)
        cleaned_size = len(cleaned)
        reduction_pct = ((original_size - cleaned_size) / original_size) * 100
        
        return {
            'original_size': original_size,
            'cleaned_size': cleaned_size,
            'reduction_bytes': original_size - cleaned_size,
            'reduction_percent': round(reduction_pct, 2)
        }


def clean_html_generic(html: str) -> str:
    """
    Generic HTML cleaning for LLM processing.
    Use this as a fallback when no site-specific extractor is available.
    
    Args:
        html: Raw HTML string
        
    Returns:
        Cleaned HTML string
    """
    cleaner = HTMLCleaner(html)
    return cleaner.clean()
