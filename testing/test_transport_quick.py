"""
Quick test for transportation extraction.
Usage: python test_transport_quick.py
"""

import os
import sys
import django

# Load environment variables
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.llm.extraction import extract_content_data
from core.llm.page_type_detection import detect_page_type, detect_content_type
from core.scraping.scraper import scrape_url
import json


# Test URL - Change this to test different pages
# Note: Rome2Rio requires Scrapfly. Try simpler sites for testing.
# Using a simple test page for now
TEST_URL = 'https://www.tripadvisor.com/ShowTopic-g309293-i792-k14177884-Transportation_from_Liberia_Airport_to_Tamarindo-Province_of_Guanacaste.html'


def main():
    print("=" * 80)
    print("🚗 QUICK TRANSPORTATION EXTRACTION TEST")
    print("=" * 80)
    print(f"\n📄 URL: {TEST_URL}\n")
    
    # Step 1: Scrape
    print("⏳ Scraping page...")
    print("🌐 Opening browser window (you can see it!)...")
    result = scrape_url(TEST_URL, headless=False)  # ← VISIBLE browser
    html = result['html']
    print(f"✅ Scraped {len(html):,} characters\n")
    
    # Step 2: Detect content type
    print("🔍 Detecting content type...")
    content_result = detect_content_type(TEST_URL, html)
    content_type = content_result['content_type']
    print(f"✅ Content Type: {content_type} ({content_result['confidence']:.0%})\n")
    
    # Step 3: Detect page type
    print("🔍 Detecting page type...")
    page_result = detect_page_type(TEST_URL, html, content_type)
    page_type = page_result['page_type']
    print(f"✅ Page Type: {page_type} ({page_result['confidence']:.0%})\n")
    
    # Step 4: Extract data
    print("⚙️  Extracting data...")
    data = extract_content_data(
        content=html,
        content_type=content_type,
        page_type=page_type,
        url=TEST_URL
    )
    print("✅ Extraction complete!\n")
    
    # Step 5: Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if page_type == 'general':
        print(f"\n🚦 Route: {data.get('origin', 'N/A')} → {data.get('destination', 'N/A')}")
        
        if data.get('distance_km'):
            print(f"📏 Distance: {data['distance_km']} km")
        
        route_options = data.get('route_options', [])
        if route_options:
            print(f"\n🚗 Found {len(route_options)} transport options:")
            for i, option in enumerate(route_options, 1):
                print(f"\n  {i}. {option.get('transport_type', 'N/A').upper()}")
                if option.get('transport_name'):
                    print(f"     Name: {option['transport_name']}")
                if option.get('price_usd'):
                    print(f"     Price: ${option['price_usd']}")
                if option.get('duration_hours'):
                    print(f"     Duration: {option['duration_hours']} hours")
        
        if data.get('fastest_option'):
            print(f"\n⚡ Fastest: {data['fastest_option'].get('type')}")
        if data.get('cheapest_option'):
            print(f"💵 Cheapest: {data['cheapest_option'].get('type')}")
        if data.get('recommended_option'):
            print(f"⭐ Recommended: {data['recommended_option'].get('type')}")
    
    else:  # specific
        print(f"\n📛 Service: {data.get('transport_name', 'N/A')}")
        print(f"🚌 Type: {data.get('transport_type', 'N/A')}")
        print(f"🗺️  Route: {data.get('route', 'N/A')}")
        if data.get('price_usd'):
            print(f"💰 Price: ${data['price_usd']}")
        if data.get('duration_hours'):
            print(f"⏱️  Duration: {data['duration_hours']} hours")
    
    print(f"\n🎯 Confidence: {data.get('extraction_confidence', 0):.0%}")
    
    # Save results
    filename = 'transport_test_result.json'
    with open(filename, 'w') as f:
        json.dump({
            'url': TEST_URL,
            'content_type': content_type,
            'page_type': page_type,
            'data': data
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Full results saved to: {filename}")
    print("\n✅ Test complete!")


if __name__ == '__main__':
    main()
