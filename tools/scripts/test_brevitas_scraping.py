#!/usr/bin/env python3
"""
Test script for scraping brevitas.com properties.
Shows the complete scraping process step by step WITHOUT Scrapfly.
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
    print(f"✓ Loaded environment from: {env_path}")

# Disable Scrapfly for this test
os.environ['SCRAPFLY_ENABLED'] = 'False'

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from core.scraping.scraper import WebScraper
from core.llm.extraction import PropertyExtractor

# Test URLs
TEST_URLS = [
    "https://brevitas.com/p/5jTTF1iWpO/oceanview-estate-ideal-for-residence-retreats-or-boutique-use-esparza",
    # Add more URLs here to test multiple properties
]

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---\n")

async def test_scraping_process():
    """Test the complete scraping process for brevitas.com"""
    
    print_section("BREVITAS.COM SCRAPING TEST")
    print(f"Testing {len(TEST_URLS)} URL(s)")
    
    for idx, url in enumerate(TEST_URLS, 1):
        print_section(f"Property {idx}/{len(TEST_URLS)}: {url}")
        
        try:
            # Step 1: Initialize scraper
            print_subsection("Step 1: Initialize Web Scraper")
            scraper = WebScraper()
            print("✓ Scraper initialized")
            
            # Step 2: Scrape the page
            print_subsection("Step 2: Scrape HTML Content")
            print(f"Fetching: {url}")
            
            result = await scraper.scrape(url)
            
            print(f"✓ Scraping completed")
            print(f"  - Method used: {result.get('method', 'unknown')}")
            print(f"  - Success: {result.get('success', False)}")
            print(f"  - HTML length: {len(result.get('html', ''))} characters")
            
            if result.get('metadata'):
                meta = result['metadata']
                print(f"  - Metadata:")
                if 'api_credits_used' in meta:
                    print(f"    • API credits used: {meta['api_credits_used']}")
                if 'proxy_type' in meta:
                    print(f"    • Proxy type: {meta['proxy_type']}")
                if 'cloudflare_bypass' in meta:
                    print(f"    • Cloudflare bypass: {meta['cloudflare_bypass']}")
            
            if not result.get('success'):
                print(f"✗ Scraping failed: {result.get('error', 'Unknown error')}")
                continue
            
            html_content = result.get('html', '')
            if len(html_content) < 1000:
                print(f"⚠ Warning: HTML content is very short ({len(html_content)} chars)")
            
            # Step 3: Show HTML preview
            print_subsection("Step 3: HTML Content Preview")
            preview_length = 500
            html_preview = html_content[:preview_length]
            print(f"First {preview_length} characters:")
            print("-" * 80)
            print(html_preview)
            if len(html_content) > preview_length:
                print(f"\n... ({len(html_content) - preview_length} more characters)")
            print("-" * 80)
            
            # Step 4: Extract property data
            print_subsection("Step 4: Extract Property Data with LLM")
            print("Sending HTML to OpenAI GPT-4o-mini for extraction...")
            
            extractor = PropertyExtractor()
            data = extractor.extract_from_html(
                html=html_content,
                url=url
            )
            
            print(f"✓ Extraction completed")
            print(f"  - Tokens used: {data.get('tokens_used', 'N/A')}")
            
            # Step 5: Display extracted data
            print_subsection("Step 5: Extracted Property Data")
            
            # Basic info
            print("BASIC INFORMATION:")
            print(f"  Title: {data.get('title', data.get('property_name', 'N/A'))}")
            print(f"  Property Type: {data.get('property_type', 'N/A')}")
            print(f"  Listing Type: {data.get('listing_type', data.get('listing_status', 'N/A'))}")
            
            # Price
            print("\nPRICE:")
            price_usd = data.get('price_usd')
            if price_usd:
                print(f"  USD: ${price_usd:,.2f}")
            else:
                print(f"  USD: N/A")
            
            # Location
            print("\nLOCATION:")
            print(f"  Address: {data.get('address', data.get('location', 'N/A'))}")
            print(f"  City: {data.get('city', 'N/A')}")
            print(f"  Province: {data.get('province', 'N/A')}")
            print(f"  Country: {data.get('country', 'N/A')}")
            
            # Features
            print("\nFEATURES:")
            print(f"  Bedrooms: {data.get('bedrooms', 'N/A')}")
            print(f"  Bathrooms: {data.get('bathrooms', 'N/A')}")
            print(f"  Area: {data.get('square_meters', 'N/A')} m²")
            print(f"  Lot Size: {data.get('lot_size_m2', 'N/A')} m²")
            
            # Description
            description = data.get('description', '')
            if description:
                print("\nDESCRIPTION:")
                print(f"  {description[:200]}...")
                print(f"  (Total length: {len(description)} characters)")
            
            # Images
            images = data.get('images', [])
            print(f"\nIMAGES: {len(images)} found")
            if images:
                for i, img in enumerate(images[:3], 1):
                    print(f"  {i}. {img}")
                if len(images) > 3:
                    print(f"  ... and {len(images) - 3} more")
            
            # Contact
            print("\nCONTACT:")
            print(f"  Agent Name: {data.get('agent_name', 'N/A')}")
            print(f"  Agent Phone: {data.get('agent_phone', 'N/A')}")
            print(f"  Agent Email: {data.get('agent_email', 'N/A')}")
            
            # Amenities
            amenities = data.get('amenities', [])
            if amenities:
                print(f"\nAMENITIES: {len(amenities)}")
                for amenity in amenities[:5]:
                    print(f"  • {amenity}")
                if len(amenities) > 5:
                    print(f"  ... and {len(amenities) - 5} more")
            
            # Metadata
            print("\nMETADATA:")
            print(f"  Source URL: {data.get('source_url', 'N/A')}")
            print(f"  Source Website: {data.get('source_website', 'N/A')}")
            print(f"  Confidence Score: {data.get('extraction_confidence', 'N/A')}")
            
            # Step 6: Save results
            print_subsection("Step 6: Save Results")
            
            output_dir = Path(__file__).parent.parent.parent / 'testing' / 'responses'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f'brevitas_test_{idx}.json'
            
            full_result = {
                'url': url,
                'scraping': {
                    'success': result.get('success'),
                    'method': result.get('method'),
                    'html_length': len(html_content),
                    'metadata': result.get('metadata', {})
                },
                'extraction': data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(full_result, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✓ Results saved to: {output_file}")
            
            print_subsection("✓ Test Complete for This URL")
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            print("\nTraceback:")
            traceback.print_exc()
    
    print_section("ALL TESTS COMPLETE")

if __name__ == '__main__':
    print("\n🚀 Starting Brevitas.com Scraping Test (WITHOUT Scrapfly)\n")
    print("This script will:")
    print("  1. Initialize the web scraper (Playwright or httpx)")
    print("  2. Scrape HTML content from brevitas.com")
    print("  3. Show HTML preview")
    print("  4. Extract property data using GPT-4o-mini")
    print("  5. Display all extracted fields")
    print("  6. Save results to JSON file")
    
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print(f"\n⚠ Warning: Missing OPENAI_API_KEY environment variable")
        print("Property extraction may not work properly.")
    
    print("\nNote: Scrapfly is DISABLED for this test")
    print("Will use Playwright (with browser) or httpx (simple GET request)")
    print("\nPress Ctrl+C to cancel...")
    
    try:
        asyncio.run(test_scraping_process())
    except KeyboardInterrupt:
        print("\n\n✗ Test cancelled by user")
        sys.exit(1)
