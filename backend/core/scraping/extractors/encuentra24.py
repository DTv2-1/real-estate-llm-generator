"""
Encuentra24.com specific extractor.
"""

from typing import Optional
from bs4 import BeautifulSoup
from decimal import Decimal
import re
from .base import BaseExtractor


class Encuentra24Extractor(BaseExtractor):
    """Extractor for encuentra24.com listings."""
    
    def __init__(self):
        super().__init__()
        self.site_name = "encuentra24.com"
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property title from Encuentra24."""
        # Try property-detail section
        title = soup.find('h1', class_='property-detail')
        if title:
            return title.get_text(strip=True)
        
        # Try property-info section
        title = soup.find('h1', class_='property-info')
        if title:
            return title.get_text(strip=True)
        
        return super().extract_title(soup)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract price from property details."""
        # Look in property-detail or property-info sections
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            section = soup.find(class_=class_name)
            if section:
                # Look for price patterns
                price_text = section.get_text()
                match = re.search(r'\$\s*([\d,]+)', price_text)
                if match:
                    price_str = match.group(1).replace(',', '')
                    try:
                        return Decimal(price_str)
                    except:
                        pass
        
        return super().extract_price(soup)
    
    def extract_bedrooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract bedrooms from property details."""
        # Search in property sections
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            section = soup.find(class_=class_name)
            if section:
                text = section.get_text()
                match = re.search(r'(\d+)\s*(habitacion|bedroom|dormitorio)', text, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        
        return super().extract_bedrooms(soup)
    
    def extract_bathrooms(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract bathrooms from property details."""
        # Search in property sections
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            section = soup.find(class_=class_name)
            if section:
                text = section.get_text()
                match = re.search(r'(\d+\.?\d*)\s*(baño|bathroom)', text, re.IGNORECASE)
                if match:
                    return Decimal(match.group(1))
        
        return super().extract_bathrooms(soup)
    
    def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property description."""
        # Try property-detail or listing-detail sections
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            desc = soup.find('div', class_=class_name)
            if desc:
                # Find paragraphs within
                paragraphs = desc.find_all('p')
                if paragraphs:
                    return '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        return super().extract_description(soup)
    
    # TODO: Add more specific methods as needed based on encuentra24 structure
