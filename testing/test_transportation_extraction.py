"""
Test Transportation Extraction System
Tests both specific (single service) and general (comparison/guide) pages.
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


# ============================================================================
# TEST URLs
# ============================================================================

TEST_URLS = {
    'general': [
        {
            'url': 'https://www.tripadvisor.com/ShowTopic-g309293-i792-k14177884-Transportation_from_Liberia_Airport_to_Tamarindo-Province_of_Guanacaste.html',
            'description': 'TripAdvisor - Transportation discussion (general)',
            'expected_page_type': 'general',
        },
    ],
    'specific': [
        {
            'url': 'https://www.costarica.com/shuttles/',
            'description': 'CostaRica.com - Shuttle services',
            'expected_page_type': 'specific',
        },
    ]
}


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_separator(char="-"):
    """Print separator line."""
    print(char * 80)


def test_content_type_detection(url, html):
    """Test content type detection."""
    print_header("STEP 1: CONTENT TYPE DETECTION")
    
    result = detect_content_type(url, html)
    
    print(f"✅ Detected Content Type: {result['content_type']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"   Method: {result['method']}")
    print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
    
    return result['content_type']


def test_page_type_detection(url, html, content_type):
    """Test page type detection."""
    print_header("STEP 2: PAGE TYPE DETECTION")
    
    result = detect_page_type(url, html, content_type)
    
    print(f"✅ Detected Page Type: {result['page_type']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"   Method: {result['method']}")
    print(f"   Indicators: {result.get('indicators', [])}")
    
    return result['page_type']


def test_extraction(url, html, content_type, page_type):
    """Test data extraction."""
    print_header("STEP 3: DATA EXTRACTION")
    
    print(f"Extracting with:")
    print(f"  - Content Type: {content_type}")
    print(f"  - Page Type: {page_type}")
    print()
    
    data = extract_content_data(
        content=html,
        content_type=content_type,
        page_type=page_type,
        url=url
    )
    
    return data


def display_results(data, page_type):
    """Display extraction results."""
    print_header("STEP 4: EXTRACTION RESULTS")
    
    if page_type == 'specific':
        display_specific_results(data)
    else:
        display_general_results(data)


def display_specific_results(data):
    """Display results for specific transport service."""
    print("\n🚗 SPECIFIC TRANSPORT SERVICE:")
    print_separator("-")
    
    print(f"\n📛 Service Name: {data.get('transport_name', 'N/A')}")
    print(f"🚌 Type: {data.get('transport_type', 'N/A')}")
    print(f"🗺️  Route: {data.get('route', 'N/A')}")
    
    price = data.get('price_usd')
    if price:
        print(f"\n💰 Price: ${price} USD")
    
    price_details = data.get('price_details', {})
    if price_details:
        print(f"   Price Details:")
        if price_details.get('one_way'):
            print(f"     - One way: ${price_details['one_way']}")
        if price_details.get('round_trip'):
            print(f"     - Round trip: ${price_details['round_trip']}")
        if price_details.get('per_person'):
            print(f"     - Per person: ${price_details['per_person']}")
        if price_details.get('note'):
            print(f"     - Note: {price_details['note']}")
    
    duration = data.get('duration_hours')
    if duration:
        print(f"\n⏱️  Duration: {duration} hours")
    
    schedule = data.get('schedule')
    if schedule:
        print(f"📅 Schedule: {schedule}")
    
    frequency = data.get('frequency')
    if frequency:
        print(f"🔄 Frequency: {frequency}")
    
    pickup = data.get('pickup_location')
    if pickup:
        print(f"\n📍 Pickup: {pickup}")
    
    dropoff = data.get('dropoff_location')
    if dropoff:
        print(f"📍 Dropoff: {dropoff}")
    
    contact = data.get('contact_phone')
    if contact:
        print(f"\n📞 Contact: {contact}")
    
    booking = data.get('booking_required')
    if booking is not None:
        print(f"📝 Booking Required: {'Yes' if booking else 'No'}")
    
    luggage = data.get('luggage_allowance')
    if luggage:
        print(f"🧳 Luggage: {luggage}")
    
    tips = data.get('tips', [])
    if tips:
        print(f"\n💡 Tips:")
        for tip in tips[:3]:
            print(f"   - {tip}")
    
    confidence = data.get('extraction_confidence', 0)
    print(f"\n🎯 Confidence: {confidence:.0%}")


def display_general_results(data):
    """Display results for general transport guide."""
    print("\n🗺️  TRANSPORT GUIDE (GENERAL):")
    print_separator("-")
    
    print(f"\n🚦 Route: {data.get('origin', 'N/A')} → {data.get('destination', 'N/A')}")
    
    distance = data.get('distance_km')
    if distance:
        print(f"📏 Distance: {distance} km")
    
    overview = data.get('overview')
    if overview:
        print(f"\n📝 Overview:")
        print(f"   {overview[:200]}..." if len(overview) > 200 else f"   {overview}")
    
    route_options = data.get('route_options', [])
    if route_options:
        print(f"\n🚗 Transport Options ({len(route_options)}):")
        print_separator("-")
        
        for i, option in enumerate(route_options[:5], 1):
            print(f"\n{i}. {option.get('transport_type', 'N/A').upper()}")
            if option.get('transport_name'):
                print(f"   Name: {option['transport_name']}")
            if option.get('price_usd'):
                print(f"   💰 Price: ${option['price_usd']} USD")
            if option.get('duration_hours'):
                print(f"   ⏱️  Duration: {option['duration_hours']} hours")
            if option.get('description'):
                desc = option['description']
                print(f"   📝 {desc[:100]}..." if len(desc) > 100 else f"   📝 {desc}")
    
    fastest = data.get('fastest_option')
    if fastest:
        print(f"\n⚡ Fastest Option: {fastest.get('type')} ({fastest.get('duration_hours')}h)")
    
    cheapest = data.get('cheapest_option')
    if cheapest:
        print(f"💵 Cheapest Option: {cheapest.get('type')} (${cheapest.get('price_usd')})")
    
    recommended = data.get('recommended_option')
    if recommended:
        print(f"⭐ Recommended: {recommended.get('type')}")
        if recommended.get('reason'):
            print(f"   Reason: {recommended['reason']}")
    
    travel_tips = data.get('travel_tips', [])
    if travel_tips:
        print(f"\n💡 Travel Tips:")
        for tip in travel_tips[:3]:
            print(f"   - {tip}")
    
    confidence = data.get('extraction_confidence', 0)
    print(f"\n🎯 Confidence: {confidence:.0%}")


def run_full_test(url, description, expected_page_type):
    """Run full test pipeline."""
    print("\n\n")
    print("=" * 80)
    print(f"🧪 TESTING: {description}")
    print(f"📄 URL: {url}")
    print("=" * 80)
    
    try:
        # Step 1: Scrape
        print("\n⏳ Scraping page...")
        result = scrape_url(url)
        html = result['html']
        print(f"✅ Scraped {len(html):,} characters")
        
        # Step 2: Detect content type
        content_type = test_content_type_detection(url, html)
        
        # Step 3: Detect page type
        page_type = test_page_type_detection(url, html, content_type)
        
        # Step 4: Extract data
        data = test_extraction(url, html, content_type, page_type)
        
        # Step 5: Display results
        display_results(data, page_type)
        
        # Step 6: Validation
        print_header("VALIDATION")
        print(f"Expected page type: {expected_page_type}")
        print(f"Actual page type: {page_type}")
        
        if page_type == expected_page_type:
            print("✅ PASS: Page type detected correctly!")
        else:
            print("❌ FAIL: Page type mismatch!")
        
        # Save to file
        filename = f"transport_extraction_{page_type}_{url.split('/')[-1][:30]}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Results saved to: {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all transportation extraction tests."""
    print("\n" + "=" * 80)
    print("🚗 TRANSPORTATION EXTRACTION TEST SUITE")
    print("=" * 80)
    
    print("\n🎯 Testing Strategy:")
    print("   1. Test GENERAL pages (Rome2Rio - multiple options)")
    print("   2. Test SPECIFIC pages (Interbus - single service)")
    print("   3. Validate page type detection")
    print("   4. Validate data extraction")
    
    input("\n⏸️  Press ENTER to start tests...")
    
    # Test general pages
    print("\n\n")
    print("🔵" * 40)
    print("TESTING GENERAL TRANSPORT GUIDES (Multiple Options)")
    print("🔵" * 40)
    
    for test_case in TEST_URLS['general']:
        success = run_full_test(
            test_case['url'],
            test_case['description'],
            test_case['expected_page_type']
        )
        if not success:
            print("\n⚠️  Test failed, but continuing...")
        input("\n⏸️  Press ENTER to continue to next test...")
    
    # Test specific pages
    print("\n\n")
    print("🟢" * 40)
    print("TESTING SPECIFIC TRANSPORT SERVICES (Single Service)")
    print("🟢" * 40)
    
    for test_case in TEST_URLS['specific']:
        success = run_full_test(
            test_case['url'],
            test_case['description'],
            test_case['expected_page_type']
        )
        if not success:
            print("\n⚠️  Test failed, but continuing...")
        input("\n⏸️  Press ENTER to continue...")
    
    print("\n\n")
    print("=" * 80)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
