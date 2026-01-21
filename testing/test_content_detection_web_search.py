"""
Test content type detection with Web Search
"""

import os
import sys
import django
import asyncio

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.llm.content_detection import detect_content_type
from core.scraping.scraper import WebScraper

async def test_detection_with_web_search():
    """Test content type detection using web search"""
    
    test_urls = [
        {
            'url': 'https://www.tripadvisor.com/Attraction_Review-g309293-d2461468-Reviews-Costa_Rica_Surf_School-Tamarindo_Province_of_Guanacaste.html',
            'expected': 'tour',
            'description': 'TripAdvisor Surf School'
        },
        {
            'url': 'https://www.encuentra24.com/costa-rica-es/bienes-raices-venta-casas-alajuela/casa-en-venta-alajuela-alajuela/19234567',
            'expected': 'real_estate',
            'description': 'Encuentra24 Property'
        },
        {
            'url': 'https://www.costarica.org/transportation/san-jose-to-tamarindo/',
            'expected': 'transportation',
            'description': 'Transportation Guide'
        }
    ]
    
    print("\n" + "="*80)
    print("🔍 TESTING CONTENT TYPE DETECTION WITH WEB SEARCH")
    print("="*80 + "\n")
    
    scraper = WebScraper()
    
    for test_case in test_urls:
        print(f"\n{'='*80}")
        print(f"📝 Test: {test_case['description']}")
        print(f"🌐 URL: {test_case['url']}")
        print(f"🎯 Expected: {test_case['expected']}")
        print(f"{'='*80}\n")
        
        # Scrape the page first
        print("📥 Scraping page...")
        scrape_result = await scraper.scrape(test_case['url'])
        
        if not scrape_result['success']:
            print(f"❌ Scraping failed: {scrape_result.get('error')}")
            continue
        
        print(f"✅ Scraped {len(scrape_result['html']):,} chars\n")
        
        # Detect content type
        print("🔎 Detecting content type...")
        detection_result = detect_content_type(
            url=test_case['url'],
            html=scrape_result['html'],
            user_override=None,  # No override, let it auto-detect
            use_llm_fallback=False
        )
        
        # Show results
        detected_type = detection_result['content_type']
        confidence = detection_result['confidence']
        method = detection_result['method']
        
        print(f"\n📊 RESULTS:")
        print(f"  Detected Type: {detected_type}")
        print(f"  Expected Type: {test_case['expected']}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Method: {method}")
        
        if detected_type == test_case['expected']:
            print(f"  ✅ CORRECT DETECTION!")
        else:
            print(f"  ❌ INCORRECT (expected {test_case['expected']})")
        
        # Show web search context if available
        if method == 'web_search':
            print(f"\n🌐 Web Search Context:")
            reasoning = detection_result.get('reasoning', '')
            print(f"  {reasoning[:300]}...")
            
            sources = detection_result.get('sources', [])
            if sources:
                print(f"\n📚 Sources ({len(sources)}):")
                for i, source in enumerate(sources[:5], 1):
                    print(f"  {i}. {source}")
        
        print()
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)


async def test_detection_comparison():
    """Compare web search vs traditional methods"""
    
    url = "https://www.tripadvisor.com/Attraction_Review-g309293-d2461468-Reviews-Costa_Rica_Surf_School-Tamarindo_Province_of_Guanacaste.html"
    
    print("\n" + "="*80)
    print("🔍 COMPARING DETECTION METHODS")
    print("="*80 + "\n")
    
    print(f"URL: {url}\n")
    
    # Scrape
    scraper = WebScraper()
    scrape_result = await scraper.scrape(url)
    
    if not scrape_result['success']:
        print(f"❌ Scraping failed")
        return
    
    html = scrape_result['html']
    
    # Test 1: With web search enabled
    print("1️⃣ WITH WEB SEARCH (WEB_SEARCH_ENABLED=True)")
    print("-" * 80)
    
    os.environ['WEB_SEARCH_ENABLED'] = 'True'
    from django.conf import settings
    settings.WEB_SEARCH_ENABLED = True
    
    result_with_web = detect_content_type(url, html, use_llm_fallback=False)
    
    print(f"  Type: {result_with_web['content_type']}")
    print(f"  Confidence: {result_with_web['confidence']:.2%}")
    print(f"  Method: {result_with_web['method']}")
    
    if result_with_web['method'] == 'web_search':
        sources = result_with_web.get('sources', [])
        print(f"  Sources: {len(sources)}")
    
    # Test 2: Without web search
    print("\n2️⃣ WITHOUT WEB SEARCH (Traditional Methods)")
    print("-" * 80)
    
    os.environ['WEB_SEARCH_ENABLED'] = 'False'
    settings.WEB_SEARCH_ENABLED = False
    
    # Force reimport to reset singleton
    import importlib
    import core.llm.content_detection
    importlib.reload(core.llm.content_detection)
    from core.llm.content_detection import detect_content_type as detect_traditional
    
    result_traditional = detect_traditional(url, html, use_llm_fallback=False)
    
    print(f"  Type: {result_traditional['content_type']}")
    print(f"  Confidence: {result_traditional['confidence']:.2%}")
    print(f"  Method: {result_traditional['method']}")
    
    # Comparison
    print("\n📊 COMPARISON")
    print("-" * 80)
    
    if result_with_web['content_type'] == result_traditional['content_type']:
        print(f"  ✅ Same result: {result_with_web['content_type']}")
    else:
        print(f"  ⚠️ Different results:")
        print(f"    Web Search: {result_with_web['content_type']}")
        print(f"    Traditional: {result_traditional['content_type']}")
    
    print(f"\n  Confidence Improvement: {result_with_web['confidence'] - result_traditional['confidence']:.2%}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test content detection with web search')
    parser.add_argument('--test', choices=['detection', 'comparison', 'all'], 
                       default='detection', help='Which test to run')
    
    args = parser.parse_args()
    
    if args.test in ['detection', 'all']:
        asyncio.run(test_detection_with_web_search())
    
    if args.test in ['comparison', 'all']:
        asyncio.run(test_detection_comparison())
