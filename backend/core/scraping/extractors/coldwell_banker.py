"""
ColdwellBankerCostaRica.com specific extractor.
"""

from typing import Optional
from bs4 import BeautifulSoup
from decimal import Decimal
import re
from .base import BaseExtractor


class ColdwellBankerExtractor(BaseExtractor):
    """Extractor for coldwellbankercostarica.com listings."""
    
    def __init__(self):
        super().__init__()
        self.site_name = "coldwellbankercostarica.com"
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property title."""
        # Try title-wrap section
        title_section = soup.find('div', class_='title-wrap')
        if title_section:
            title = title_section.find('h1')
            if title:
                return title.get_text(strip=True)
        
        return super().extract_title(soup)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract price from title-wrap section."""
        title_section = soup.find('div', class_='title-wrap')
        if title_section:
            price_text = title_section.get_text()
            match = re.search(r'\$\s*([\d,]+)', price_text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return Decimal(price_str)
                except:
                    pass
        
        return super().extract_price(soup)
    
    def extract_bedrooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract bedrooms from ul-specs."""
        specs = soup.find('ul', class_='ul-specs')
        if specs:
            text = specs.get_text()
            match = re.search(r'(\d+)\s*(bed|habitacion|dormitorio)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Try more-details section
        more_details = soup.find('div', class_='more-details')
        if more_details:
            text = more_details.get_text()
            match = re.search(r'(\d+)\s*(bed|habitacion|dormitorio)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return super().extract_bedrooms(soup)
    
    def extract_bathrooms(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract bathrooms from ul-specs."""
        specs = soup.find('ul', class_='ul-specs')
        if specs:
            text = specs.get_text()
            match = re.search(r'(\d+\.?\d*)\s*(bath|baño)', text, re.IGNORECASE)
            if match:
                return Decimal(match.group(1))
        
        # Try more-details section
        more_details = soup.find('div', class_='more-details')
        if more_details:
            text = more_details.get_text()
            match = re.search(r'(\d+\.?\d*)\s*(bath|baño)', text, re.IGNORECASE)
            if match:
                return Decimal(match.group(1))
        
        return super().extract_bathrooms(soup)
    
    def extract_area(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract building area from specs."""
        specs = soup.find('ul', class_='ul-specs')
        if specs:
            text = specs.get_text()
            # Look for sq ft or m2
            match = re.search(r'([\d,]+\.?\d*)\s*(sq\s*ft|sqft|m[²2])', text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = Decimal(value_str)
                    # Convert sq ft to m2 if needed
                    if 'ft' in match.group(2).lower():
                        value = value * Decimal('0.092903')
                    return value
                except:
                    pass
        
        return super().extract_area(soup)
    
    def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property description."""
        desc = soup.find('div', class_='property-description')
        if desc:
            return desc.get_text(separator='\n', strip=True)
        
        return super().extract_description(soup)
    
    def extract_amenities(self, soup: BeautifulSoup) -> list:
        """Extract amenities from property-features."""
        amenities = []
        features_section = soup.find('div', class_='property-features')
        if features_section:
            # Find list items
            items = features_section.find_all('li')
            for item in items:
                amenity = item.get_text(strip=True)
                if amenity:
                    amenities.append(amenity)
        
        return amenities if amenities else super().extract_amenities(soup)
    
    def extract_latitude(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract latitude from map iframe."""
        # Look for Google Maps iframe
        iframe = soup.find('iframe', src=lambda x: x and 'google.com/maps' in x)
        if iframe:
            src = iframe.get('src', '')
            # Extract coordinates from iframe src
            # Format: https://maps.google.com/maps?q=LAT,LNG&...
            match = re.search(r'[?&]q=([-\d.]+),([-\d.]+)', src)
            if match:
                try:
                    return Decimal(match.group(1))
                except:
                    pass
        
        # Try map-container data attributes
        map_container = soup.find('div', class_='map-container')
        if map_container:
            lat = map_container.get('data-lat') or map_container.get('data-latitude')
            if lat:
                try:
                    return Decimal(lat)
                except:
                    pass
        
        return super().extract_latitude(soup)
    
    def extract_longitude(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract longitude from map iframe."""
        # Look for Google Maps iframe
        iframe = soup.find('iframe', src=lambda x: x and 'google.com/maps' in x)
        if iframe:
            src = iframe.get('src', '')
            match = re.search(r'[?&]q=([-\d.]+),([-\d.]+)', src)
            if match:
                try:
                    return Decimal(match.group(2))
                except:
                    pass
        
        # Try map-container data attributes
        map_container = soup.find('div', class_='map-container')
        if map_container:
            lng = map_container.get('data-lng') or map_container.get('data-longitude')
            if lng:
                try:
                    return Decimal(lng)
                except:
                    pass
        
        return super().extract_longitude(soup)
    
    def extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address from location-wrap."""
        location_section = soup.find('div', class_='location-wrap')
        if location_section:
            # Try to find address in the section
            addr = location_section.find('address')
            if addr:
                return addr.get_text(strip=True)
            
            # Or try paragraphs
            paragraphs = location_section.find_all('p')
            if paragraphs:
                return paragraphs[0].get_text(strip=True)
        
        return super().extract_address(soup)
