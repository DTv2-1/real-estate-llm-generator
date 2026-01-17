"""
Base extractor class for property data extraction.
Also includes generic HTML cleaning utilities.
"""

from typing import Dict, Optional, List, Any
from bs4 import BeautifulSoup
from decimal import Decimal
import re
from ..types import PropertyData

def clean_html_generic(html: str) -> str:
    """
    Generic HTML cleaning for better text extraction.
    Removes scripts, styles, ads, and unnecessary elements.
    
    This is used as a fallback when no site-specific extractor is available,
    or when you need to clean HTML before processing.
    
    Args:
        html: Raw HTML string
        
    Returns:
        Cleaned HTML string with reduced size (typically 70-90% reduction)
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Elements to remove
    REMOVE_TAGS = [
        'script', 'style', 'link', 'meta', 'noscript', 
        'iframe', 'svg', 'path', 'g', 'defs',
        'header', 'footer', 'nav', 'aside'
    ]
    
    # Remove unnecessary tags
    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    
    # Remove elements by pattern (ads, cookies, etc.)
    REMOVE_PATTERNS = [
        r'cookie', r'gdpr', r'popup', r'modal', r'advertisement',
        r'social-share', r'newsletter', r'subscribe', r'footer',
        r'header', r'navigation', r'menu', r'sidebar',
        r'recaptcha', r'captcha', r'tracking', r'analytics'
    ]
    
    elements = list(soup.find_all(True))
    for element in elements:
        if not element or not element.parent:
            continue
            
        # Check class and id attributes
        try:
            classes = element.get('class', [])
            class_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
        except (AttributeError, TypeError):
            class_str = ''
        
        try:
            elem_id = element.get('id', '')
        except (AttributeError, TypeError):
            elem_id = ''
        
        combined = f"{class_str} {elem_id}".lower()
        
        # Remove if matches any pattern
        for pattern in REMOVE_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                try:
                    element.decompose()
                except:
                    pass
                break
    
    # Clean attributes (keep only essential ones)
    KEEP_ATTRS = ['class', 'id', 'href', 'src', 'alt', 'title']
    for tag in soup.find_all(True):
        if not tag or not tag.parent:
            continue
            
        try:
            attrs = dict(tag.attrs)
            for attr in list(attrs.keys()):
                if attr not in KEEP_ATTRS:
                    try:
                        del tag.attrs[attr]
                    except (KeyError, AttributeError):
                        pass
        except (AttributeError, TypeError):
            continue
    
    # Remove empty elements
    for element in soup.find_all(True):
        if element.name in ['br', 'hr', 'img', 'input']:
            continue
            
        if not element.get_text(strip=True) and not element.find_all('img'):
            element.decompose()
    
    # Get cleaned HTML
    cleaned_html = str(soup)
    
    # Clean whitespace
    cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
    cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)
    
    return cleaned_html.strip()


class BaseExtractor:
    """Base class for site-specific extractors."""
    
    def __init__(self):
        self.site_name = "generic"
    
    def extract(self, html: str, url: Optional[str] = None) -> PropertyData:
        """
        Extract property data from HTML.
        
        Args:
            html: Raw HTML content
            url: Source URL
            
        Returns:
            Dictionary with extracted property data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        data = {
            'title': self.extract_title(soup),
            'price_usd': self.extract_price(soup),
            'bedrooms': self.extract_bedrooms(soup),
            'bathrooms': self.extract_bathrooms(soup),
            'area_m2': self.extract_area(soup),
            'lot_size_m2': self.extract_lot_size(soup),
            'description': self.extract_description(soup),
            'property_type': self.extract_property_type(soup),
            'listing_type': self.extract_listing_type(soup),
            'location': self.extract_location(soup),
            'address': self.extract_address(soup),
            'city': self.extract_city(soup),
            'province': self.extract_province(soup),
            'country': self.extract_country(soup),
            'latitude': self.extract_latitude(soup),
            'longitude': self.extract_longitude(soup),
            'images': self.extract_images(soup),
            'amenities': self.extract_amenities(soup),
            'agent_name': self.extract_agent_name(soup),
            'agent_phone': self.extract_agent_phone(soup),
            'agent_email': self.extract_agent_email(soup),
            'year_built': self.extract_year_built(soup),
            'parking_spaces': self.extract_parking(soup),
            'source_url': url,
            'source_website': self.site_name,
        }
        
        return data
    
    # Methods to override in subclasses
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property title."""
        # Try common patterns
        title = soup.find('h1')
        if title:
            return title.get_text(strip=True)
        
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return None
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract price in USD."""
        # Look for price patterns
        patterns = [
            r'\$\s*([\d,]+)',
            r'USD\s*([\d,]+)',
            r'Price:\s*\$\s*([\d,]+)',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return Decimal(price_str)
                except:
                    pass
        
        return None
    
    def extract_bedrooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of bedrooms."""
        patterns = [
            r'(\d+)\s*bed',
            r'Bed.*?:\s*(\d+)',
            r'Bedrooms.*?(\d+)',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def extract_bathrooms(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract number of bathrooms."""
        patterns = [
            r'(\d+\.?\d*)\s*bath',
            r'Bath.*?:\s*(\d+\.?\d*)',
            r'Bathrooms.*?(\d+\.?\d*)',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return Decimal(match.group(1))
                except:
                    pass
        
        return None
    
    def extract_area(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract building area in square meters."""
        # Look for sq ft or m2
        patterns = [
            r'([\d,]+)\s*sq\s*ft',
            r'([\d,]+)\s*sqft',
            r'([\d,]+)\s*m[²2]',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = Decimal(value_str)
                    # Convert sq ft to m2 if needed
                    if 'ft' in pattern:
                        value = value * Decimal('0.092903')
                    return value
                except:
                    pass
        
        return None
    
    def extract_lot_size(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract lot size in square meters."""
        patterns = [
            r'Lot.*?([\d,]+\.?\d*)\s*acres',
            r'Lot.*?([\d,]+\.?\d*)\s*m[²2]',
            r'Lot.*?([\d,]+\.?\d*)\s*hectares',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = Decimal(value_str)
                    # Convert to m2
                    if 'acre' in pattern.lower():
                        value = value * Decimal('4046.86')
                    elif 'hectare' in pattern.lower():
                        value = value * Decimal('10000')
                    return value
                except:
                    pass
        
        return None
    
    def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property description."""
        # Try common selectors
        desc = soup.find('div', class_=lambda x: x and 'description' in str(x).lower())
        if desc:
            return desc.get_text(strip=True)
        
        desc = soup.find('p', class_=lambda x: x and 'description' in str(x).lower())
        if desc:
            return desc.get_text(strip=True)
        
        return None
    
    def extract_property_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property type (house, condo, land, etc.)."""
        return None
    
    def extract_listing_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing type (for_sale, for_rent)."""
        return None
    
    def extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract full location string."""
        return None
    
    def extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract street address."""
        return None
    
    def extract_city(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract city."""
        return None
    
    def extract_province(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract province/state."""
        return None
    
    def extract_country(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract country."""
        return None
    
    def extract_latitude(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract latitude."""
        return None
    
    def extract_longitude(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract longitude."""
        return None
    
    def extract_images(self, soup: BeautifulSoup) -> list:
        """Extract image URLs."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and 'http' in src:
                images.append(src)
        return images
    
    def extract_amenities(self, soup: BeautifulSoup) -> list:
        """Extract amenities list."""
        return []
    
    def extract_agent_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent name."""
        return None
    
    def extract_agent_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent phone."""
        return None
    
    def extract_agent_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent email."""
        return None
    
    def extract_year_built(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract year built."""
        return None
    
    def extract_parking(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract parking spaces."""
        return None
