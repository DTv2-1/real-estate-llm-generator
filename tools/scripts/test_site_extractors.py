#!/usr/bin/env python3
"""
Test site-specific extractors.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Disable Scrapfly for this test
os.environ['SCRAPFLY_ENABLED'] = 'False'

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from core.scraping.scraper import WebScraper
from core.scraping.extractors import get_extractor

# Test URL
TEST_URL = "https://brevitas.com/p/5jTTF1iWpO/oceanview-estate-ideal-for-residence-retreats-or-boutique-use-esparza"

async def test_site_extractor():
    """Test site-specific extractor."""
    
    print("\n" + "="*80)
    print(" TESTING SITE-SPECIFIC EXTRACTOR")
    print("="*80 + "\n")
    
    print(f"URL: {TEST_URL}\n")
    
    # Step 1: Scrape HTML
    print("Step 1: Scraping HTML...")
    scraper = WebScraper()
    result = await scraper.scrape(TEST_URL)
    
    if not result.get('success'):
        print(f"✗ Scraping failed: {result.get('error')}")
        return
    
    html = result.get('html', '')
    print(f"✓ Scraped {len(html)} characters using {result.get('method')}\n")
    
    # Step 2: Get appropriate extractor
    print("Step 2: Getting site-specific extractor...")
    extractor = get_extractor(TEST_URL)
    print(f"✓ Using extractor: {extractor.__class__.__name__} for {extractor.site_name}\n")
    
    # Step 3: Extract data
    print("Step 3: Extracting property data...")
    data = extractor.extract(html, TEST_URL)
    
    # Display results
    print("\n" + "="*80)
    print(" EXTRACTED DATA")
    print("="*80 + "\n")
    
    print("BASIC INFO:")
    print(f"  Title: {data.get('title')}")
    print(f"  Property Type: {data.get('property_type')}")
    print(f"  Listing Type: {data.get('listing_type')}")
    
    print("\nPRICE:")
    price = data.get('price_usd')
    if price:
        print(f"  USD: ${price:,.2f}")
    else:
        print(f"  USD: N/A")
    
    print("\nLOCATION:")
    print(f"  Address: {data.get('address')}")
    print(f"  City: {data.get('city')}")
    print(f"  Province: {data.get('province')}")
    print(f"  Country: {data.get('country')}")
    
    print("\nFEATURES:")
    print(f"  Bedrooms: {data.get('bedrooms')}")
    print(f"  Bathrooms: {data.get('bathrooms')}")
    area = data.get('area_m2')
    if area:
        print(f"  Area: {area:.2f} m²")
    else:
        print(f"  Area: N/A")
    lot = data.get('lot_size_m2')
    if lot:
        print(f"  Lot Size: {lot:.2f} m²")
    else:
        print(f"  Lot Size: N/A")
    print(f"  Parking: {data.get('parking_spaces')}")
    
    print("\nDESCRIPTION:")
    desc = data.get('description', '')
    if desc:
        print(f"  {desc[:200]}...")
        print(f"  (Total: {len(desc)} characters)")
    else:
        print(f"  N/A")
    
    print(f"\nIMAGES: {len(data.get('images', []))} found")
    
    print(f"\nAMENITIES: {len(data.get('amenities', []))}")
    for amenity in data.get('amenities', [])[:5]:
        print(f"  • {amenity}")
    if len(data.get('amenities', [])) > 5:
        print(f"  ... and {len(data.get('amenities', [])) - 5} more")
    
    print("\nCONTACT:")
    print(f"  Agent: {data.get('agent_name')}")
    print(f"  Phone: {data.get('agent_phone')}")
    print(f"  Email: {data.get('agent_email')}")
    
    print("\nMETADATA:")
    print(f"  Source: {data.get('source_website')}")
    print(f"  URL: {data.get('source_url')}")
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / 'testing' / 'responses'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'brevitas_site_extractor_test.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✓ Results saved to: {output_file}")
    print("\n" + "="*80)
    print(" TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    asyncio.run(test_site_extractor())
