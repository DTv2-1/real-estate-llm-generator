"""
Brevitas.com specific extractor.
"""

from typing import Optional
from bs4 import BeautifulSoup
from decimal import Decimal
import re
import logging
from .base import BaseExtractor

logger = logging.getLogger(__name__)


class BrevitasExtractor(BaseExtractor):
    """Extractor for brevitas.com listings."""
    
    def __init__(self):
        super().__init__()
        self.site_name = "brevitas.com"
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property title."""
        # Brevitas uses show__title class
        title = soup.find('h1', class_='show__title')
        if title:
            return title.get_text(strip=True)
        return super().extract_title(soup)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract price from show__price."""
        # Try show__price class
        price_elem = soup.find(class_='show__price')
        if price_elem:
            text = price_elem.get_text(strip=True)
            logger.info(f"[Brevitas] Found price element: {text}")
            # Remove $ and commas
            match = re.search(r'([\d,]+)', text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price = Decimal(price_str)
                    logger.info(f"[Brevitas] Extracted price: ${price}")
                    return price
                except:
                    pass
        
        # Fallback: try to find any element with $ symbol
        all_text = soup.get_text()
        match = re.search(r'\$\s*([\d,]+)', all_text)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                price = Decimal(price_str)
                logger.info(f"[Brevitas] Extracted price from text: ${price}")
                return price
            except:
                pass
        
        logger.warning("[Brevitas] Could not find price")
        return super().extract_price(soup)
    
    def extract_bedrooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract bedrooms from Details section."""
        # Look for "Beds:" in product details
        details = soup.find_all(class_='product__detail')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'Beds:' in text or 'Bedrooms:' in text:
                match = re.search(r'(\d+)', text)
                if match:
                    return int(match.group(1))
        
        # Also check in description
        desc_elem = soup.find('p', class_='show__copy')
        if desc_elem:
            text = desc_elem.get_text()
            match = re.search(r'Bedrooms:\s*(\d+)', text)
            if match:
                return int(match.group(1))
        
        return super().extract_bedrooms(soup)
    
    def extract_bathrooms(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract bathrooms from Details section."""
        # Look for "Baths:" in product details
        details = soup.find_all(class_='product__detail')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'Baths:' in text or 'Bathrooms:' in text:
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    return Decimal(match.group(1))
        
        # Also check in description
        desc_elem = soup.find('p', class_='show__copy')
        if desc_elem:
            text = desc_elem.get_text()
            match = re.search(r'Bathrooms:\s*(\d+)', text)
            if match:
                return Decimal(match.group(1))
        
        return super().extract_bathrooms(soup)
    
    def extract_area(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract building size."""
        # Look for Building Size in details
        details = soup.find_all(class_='product__detail')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'Building Size:' in text:
                match = re.search(r'([\d,]+\.?\d*)\s*sqft', text)
                if match:
                    sqft = Decimal(match.group(1).replace(',', ''))
                    return sqft * Decimal('0.092903')  # Convert to m2
        
        # Also check description
        desc_elem = soup.find('p', class_='show__copy')
        if desc_elem:
            text = desc_elem.get_text()
            match = re.search(r'Total Construction:\s*([\d,]+)\s*sq ft', text)
            if match:
                sqft = Decimal(match.group(1).replace(',', ''))
                return sqft * Decimal('0.092903')
        
        return super().extract_area(soup)
    
    def extract_lot_size(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract lot area."""
        # Look for Lot Area in details
        details = soup.find_all(class_='product__detail')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'Lot Area:' in text:
                match = re.search(r'([\d,]+\.?\d*)\s*acres', text)
                if match:
                    acres = Decimal(match.group(1).replace(',', ''))
                    return acres * Decimal('4046.86')  # Convert to m2
        
        # Also check description
        desc_elem = soup.find('p', class_='show__copy')
        if desc_elem:
            text = desc_elem.get_text()
            match = re.search(r'Lot Size:\s*([\d,]+\.?\d*)\s*acres', text)
            if match:
                acres = Decimal(match.group(1).replace(',', ''))
                return acres * Decimal('4046.86')
        
        return super().extract_lot_size(soup)
    
    def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property description."""
        # Brevitas uses show__copy class for description
        desc = soup.find('p', class_='show__copy')
        if desc:
            return desc.get_text(separator='\n', strip=True)
        return super().extract_description(soup)
    
    def extract_property_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property type from badges."""
        badges = soup.find_all(class_='label')
        for badge in badges:
            text = badge.get_text(strip=True).lower()
            if 'residential' in text:
                # Check if it has bedrooms to determine if it's a house/condo or land
                bedrooms = self.extract_bedrooms(soup)
                if bedrooms and bedrooms > 0:
                    return 'house'
                else:
                    return 'land'
            elif 'commercial' in text:
                return 'commercial'
        return 'house'
    
    def extract_listing_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing type."""
        badges = soup.find_all(class_='label')
        for badge in badges:
            text = badge.get_text(strip=True).lower()
            if 'for sale' in text:
                return 'for_sale'
            elif 'for rent' in text or 'for lease' in text:
                return 'for_rent'
        return 'for_sale'
    
    def extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address."""
        addr = soup.find('p', class_='show__address')
        if addr:
            return addr.get_text(strip=True)
        return None
    
    def extract_city(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract city from address."""
        addr = self.extract_address(soup)
        if addr:
            # Brevitas format: "Juanilama, Espíritu Santo, Provincia de Puntarenas 60201, Costa Rica"
            parts = [p.strip() for p in addr.split(',')]
            if len(parts) >= 2:
                return parts[1]  # Espíritu Santo
        return None
    
    def extract_province(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract province from address."""
        addr = self.extract_address(soup)
        if addr:
            # Look for "Provincia de X"
            match = re.search(r'Provincia de ([^,\d]+)', addr)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_country(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract country from address."""
        addr = self.extract_address(soup)
        if addr and 'Costa Rica' in addr:
            return 'Costa Rica'
        return None
    
    def extract_parking(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract parking spaces."""
        details = soup.find_all(class_='product__detail')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'Parking Spots:' in text:
                match = re.search(r'(\d+)', text)
                if match:
                    return int(match.group(1))
        return None
    
    def extract_amenities(self, soup: BeautifulSoup) -> list:
        """Extract amenities from description."""
        amenities = []
        desc = soup.find('p', class_='show__copy')
        if desc:
            text = desc.get_text()
            
            # Look for bulleted lists
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # Lines starting with • or -
                if line.startswith('•') or line.startswith('-'):
                    amenity = line.lstrip('•-').strip()
                    if amenity and len(amenity) > 3:
                        amenities.append(amenity)
        
        return amenities
    
    def extract_agent_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent name from contact section."""
        desc = soup.find('p', class_='show__copy')
        if desc:
            text = desc.get_text()
            # Look for "Contact" section
            if 'Contact' in text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'Contact' in line and i + 2 < len(lines):
                        # Agent name is usually after "Contact"
                        agent_line = lines[i + 2].strip()
                        if agent_line and '/' in agent_line:
                            # "Evelyn Bulakar / Justin Nielsen"
                            return agent_line.split('/')[0].strip()
                        elif agent_line and not any(x in agent_line for x in ['WhatsApp', 'Email', '@', '+']):
                            return agent_line
        return None
    
    def extract_agent_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent phone."""
        desc = soup.find('p', class_='show__copy')
        if desc:
            text = desc.get_text()
            # Look for phone numbers
            match = re.search(r'\+\d{3}\s*\d{4}-\d{4}', text)
            if match:
                return match.group(0)
        return None
    
    def extract_agent_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent email."""
        desc = soup.find('p', class_='show__copy')
        if desc:
            text = desc.get_text()
            # Look for email
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            if match:
                return match.group(0)
        return None
