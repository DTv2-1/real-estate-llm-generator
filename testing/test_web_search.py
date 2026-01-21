"""
Test OpenAI Web Search integration with TripAdvisor
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.llm.web_search import get_web_search_service
from core.llm.extraction import PropertyExtractor
from core.scraping.scraper import WebScraper
import json

def test_web_search():
    """Test web search directly"""
    print("\n" + "="*80)
    print("🌐 TESTING OPENAI WEB SEARCH")
    print("="*80 + "\n")
    
    service = get_web_search_service()
    
    if not service.enabled:
        print("❌ Web search is DISABLED")
        print("Set WEB_SEARCH_ENABLED=True in .env to enable")
        return
    
    # Test query
    query = "Costa Rica Surf School Tamarindo reviews ratings prices hours location"
    
    print(f"🔍 Query: {query}\n")
    
    result = service.search(
        query=query,
        model="gpt-4o",
        country="CR"
    )
    
    if result['success']:
        print("✅ SEARCH SUCCESSFUL\n")
        print(f"📝 Answer:\n{result['answer']}\n")
        print(f"\n📚 Sources ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source}")
        
        print(f"\n🔗 Citations ({len(result['citations'])}):")
        for i, citation in enumerate(result['citations'], 1):
            print(f"  {i}. {citation.get('title', 'No title')}")
            print(f"     URL: {citation.get('url')}")
            print(f"     Text: {citation.get('text', '')[:100]}...")
    else:
        print(f"❌ SEARCH FAILED: {result.get('error')}")


def test_full_extraction_with_web_search():
    """Test full extraction pipeline with web search"""
    print("\n" + "="*80)
    print("🔍 TESTING FULL EXTRACTION WITH WEB SEARCH")
    print("="*80 + "\n")
    
    # Test URL
    url = "https://www.tripadvisor.com/Attraction_Review-g309293-d2461468-Reviews-Costa_Rica_Surf_School-Tamarindo_Province_of_Guanacaste.html"
    
    print(f"🌐 URL: {url}\n")
    
    # Step 1: Scrape with ScrapFly
    print("📥 Step 1: Scraping with ScrapFly...")
    scraper = WebScraper()
    scrape_result = scraper.scrape(url)
    
    if not scrape_result['success']:
        print(f"❌ Scraping failed: {scrape_result.get('error')}")
        return
    
    html_length = len(scrape_result['html'])
    print(f"✅ Scraped {html_length:,} chars\n")
    
    # Step 2: Extract with web search
    print("🤖 Step 2: Extracting with OpenAI + Web Search...")
    extractor = PropertyExtractor(content_type='tour', page_type='specific')
    
    try:
        extracted_data = extractor.extract_from_html(scrape_result['html'], url=url)
        
        print("✅ EXTRACTION COMPLETE\n")
        
        # Show main fields
        print("📊 EXTRACTED DATA:")
        print(f"  Tour Name: {extracted_data.get('tour_name')}")
        print(f"  Location: {extracted_data.get('location')}")
        print(f"  Price: ${extracted_data.get('price_usd')}")
        print(f"  Rating: {extracted_data.get('rating')}")
        print(f"  Duration: {extracted_data.get('duration_hours')} hours")
        print(f"  Confidence: {extracted_data.get('extraction_confidence')}")
        
        # Show web search context if available
        if 'web_search_context' in extracted_data:
            print("\n🌐 WEB SEARCH CONTEXT:")
            print(extracted_data['web_search_context'][:500] + "...")
            
            print(f"\n📚 Web Search Sources ({len(extracted_data.get('web_search_sources', []))}):")
            for i, source in enumerate(extracted_data.get('web_search_sources', [])[:5], 1):
                print(f"  {i}. {source}")
        else:
            print("\n⚠️ No web search context found")
        
        # Save to file
        output_file = 'testing/tripadvisor_with_web_search.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n💾 Saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()


def test_web_search_enrichment():
    """Test just the enrichment part with existing data"""
    print("\n" + "="*80)
    print("🔍 TESTING WEB SEARCH ENRICHMENT")
    print("="*80 + "\n")
    
    # Simulate already extracted data with missing fields
    existing_data = {
        'tour_name': 'Costa Rica Surf School',
        'location': 'Tamarindo, Costa Rica',
        'price_usd': None,  # Missing
        'rating': None,  # Missing
        'duration_hours': None,  # Missing
        'opening_hours': None,  # Missing
    }
    
    url = "https://www.tripadvisor.com/Attraction_Review-g309293-d2461468-Reviews-Costa_Rica_Surf_School-Tamarindo_Province_of_Guanacaste.html"
    
    print("📋 Existing data (with missing fields):")
    print(json.dumps(existing_data, indent=2))
    
    print("\n🌐 Enriching with web search...")
    
    service = get_web_search_service()
    enriched_data = service.enrich_property_data(
        property_data=existing_data,
        url=url,
        content_type='tour'
    )
    
    print("\n✅ ENRICHED DATA:")
    
    if 'web_search_context' in enriched_data:
        print("\n📝 Web Search Context:")
        print(enriched_data['web_search_context'])
        
        print(f"\n📚 Sources ({len(enriched_data.get('web_search_sources', []))}):")
        for source in enriched_data.get('web_search_sources', []):
            print(f"  - {source}")
    else:
        print("⚠️ No web search context added")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test OpenAI Web Search')
    parser.add_argument('--test', choices=['search', 'full', 'enrich', 'all'], 
                       default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    if args.test in ['search', 'all']:
        test_web_search()
    
    if args.test in ['enrich', 'all']:
        test_web_search_enrichment()
    
    if args.test in ['full', 'all']:
        test_full_extraction_with_web_search()
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)
