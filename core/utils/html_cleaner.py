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


class WebsiteSpecificCleaner:
    """
    Website-specific HTML extraction strategies.
    Each method knows the exact HTML structure of a specific website.
    """
    
    @staticmethod
    def extract_encuentra24(html: str) -> str:
        """
        Extract only property details section from Encuentra24.
        Targets the main property information container.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Encuentra24 typically has property details in specific containers
        relevant_selectors = [
            {'class': 'property-detail'},
            {'class': 'property-info'},
            {'id': 'property-details'},
            {'class': 'listing-detail'},
        ]
        
        extracted_parts = []
        
        for selector in relevant_selectors:
            elements = soup.find_all(attrs=selector)
            for elem in elements:
                extracted_parts.append(str(elem))
        
        # If no specific elements found, use basic cleaner
        if not extracted_parts:
            cleaner = HTMLCleaner(html)
            return cleaner.clean()
        
        combined_html = '\n'.join(extracted_parts)
        
        # Apply basic cleaning to extracted parts
        cleaner = HTMLCleaner(combined_html)
        return cleaner.clean()
    
    @staticmethod
    def extract_coldwell_banker(html: str) -> str:
        """
        Extract property details from Coldwell Banker Costa Rica.
        Focuses on property-specific content areas.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        extracted_parts = []
        
        # Title and price section
        title_section = soup.find('div', class_='title-wrap')
        if title_section:
            extracted_parts.append(str(title_section))
        
        # Property details/specs
        specs_section = soup.find('ul', class_='ul-specs')
        if specs_section:
            extracted_parts.append(str(specs_section))
        
        # More details section
        more_details = soup.find('div', class_='more-details')
        if more_details:
            extracted_parts.append(str(more_details))
        
        # Features list
        features_section = soup.find('div', class_='property-features')
        if features_section:
            extracted_parts.append(str(features_section))
        
        # Property description
        description = soup.find('div', class_='property-description')
        if description:
            extracted_parts.append(str(description))
        
        # Location information (includes map with coordinates)
        location_section = soup.find('div', class_='location-wrap')
        if location_section:
            extracted_parts.append(str(location_section))
        
        # Map container (contains iframe with coordinates)
        map_section = soup.find('div', class_='map-wrap')
        if map_section:
            extracted_parts.append(str(map_section))
        
        # Map iframe container (CRITICAL for coordinates)
        map_container = soup.find('div', class_='map-container')
        if map_container:
            print(f"✅ Found map-container: {str(map_container)[:200]}")
            extracted_parts.append(str(map_container))
        else:
            print("❌ map-container NOT FOUND")
        
        # Also try to find iframe directly
        map_iframe = soup.find('iframe', src=lambda x: x and 'google.com/maps' in x)
        if map_iframe:
            print(f"✅ Found Google Maps iframe: {str(map_iframe)[:200]}")
            extracted_parts.append(str(map_iframe))
        else:
            print("❌ Google Maps iframe NOT FOUND")
            
        # Debug: Check if ANY iframe exists
        all_iframes = soup.find_all('iframe')
        print(f"🔍 Total iframes found: {len(all_iframes)}")
        if all_iframes:
            for i, iframe in enumerate(all_iframes[:3]):  # Show first 3
                print(f"  iframe {i+1}: src={iframe.get('src', 'NO SRC')[:100]}")
        
        # If nothing found, try broader selectors
        if not extracted_parts:
            # Try to find main property row
            property_row = soup.find('section', class_='row_property_details')
            if property_row:
                extracted_parts.append(str(property_row))
        
        # If still nothing, use basic cleaner
        if not extracted_parts:
            cleaner = HTMLCleaner(html)
            return cleaner.clean()
        
        combined_html = '\n'.join(extracted_parts)
        
        # Apply basic cleaning
        cleaner = HTMLCleaner(combined_html)
        return cleaner.clean()
    
    @staticmethod
    def extract_crrealestate(html: str) -> str:
        """
        Extract property details from CR Real Estate.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        relevant_selectors = [
            {'class': 'property-details'},
            {'class': 'property-content'},
            {'id': 'property-main'},
        ]
        
        extracted_parts = []
        
        for selector in relevant_selectors:
            elements = soup.find_all(attrs=selector)
            for elem in elements:
                extracted_parts.append(str(elem))
        
        if not extracted_parts:
            cleaner = HTMLCleaner(html)
            return cleaner.clean()
        
        combined_html = '\n'.join(extracted_parts)
        cleaner = HTMLCleaner(combined_html)
        return cleaner.clean()


def clean_html_for_extraction(html: str, source_website: str = 'other') -> Dict[str, any]:
    """
    Main function to clean HTML based on source website.
    
    Args:
        html: Raw HTML string
        source_website: Website identifier (encuentra24, coldwellbanker, etc.)
    
    Returns:
        Dictionary with cleaned HTML and statistics
    """
    # Apply website-specific extraction if available
    if source_website == 'encuentra24':
        cleaned_html = WebsiteSpecificCleaner.extract_encuentra24(html)
    elif source_website == 'coldwellbanker':
        cleaned_html = WebsiteSpecificCleaner.extract_coldwell_banker(html)
    elif source_website == 'crrealestate':
        cleaned_html = WebsiteSpecificCleaner.extract_crrealestate(html)
    else:
        # Use generic cleaner for unknown sources
        cleaner = HTMLCleaner(html)
        cleaned_html = cleaner.clean()
    
    # Calculate statistics
    original_size = len(html)
    cleaned_size = len(cleaned_html)
    reduction_pct = ((original_size - cleaned_size) / original_size) * 100 if original_size > 0 else 0
    
    # Estimate token reduction (rough: 1 token ≈ 4 chars)
    original_tokens = original_size // 4
    cleaned_tokens = cleaned_size // 4
    token_reduction = original_tokens - cleaned_tokens
    
    return {
        'cleaned_html': cleaned_html,
        'original_size': original_size,
        'cleaned_size': cleaned_size,
        'reduction_bytes': original_size - cleaned_size,
        'reduction_percent': round(reduction_pct, 2),
        'estimated_original_tokens': original_tokens,
        'estimated_cleaned_tokens': cleaned_tokens,
        'estimated_token_savings': token_reduction,
        'estimated_cost_savings_usd': round((token_reduction / 1000) * 0.0025, 4)  # GPT-4 input pricing
    }
