#!/usr/bin/env python3
"""Test extraction directly without server."""
import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_file = Path(__file__).parent / '.env'
load_dotenv(env_file, override=True)

# Django setup
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.properties.models import Property
from apps.properties.models_content import LocalTipsGeneral
from core.scraping.scraper import scrape_url
from core.llm.extraction.content_detection import detect_content_type
from core.llm.extraction.page_type_detection import detect_page_type
from core.llm.extraction.extractor import PropertyExtractor
import json

print("🔄 Testing improved prompt with WikiVoyage Costa Rica...\n")

url = 'https://en.wikivoyage.org/wiki/Costa_Rica'

# 1. Scrape
print("1. Scraping...")
scrape_result = scrape_url(url)
html_content = scrape_result['content']
print(f"   ✅ Got {len(html_content)} chars\n")

# 2. Detect content type
print("2. Detecting content type...")
content_type = detect_content_type(html_content, url)
print(f"   ✅ Content type: {content_type}\n")

# 3. Detect page type  
print("3. Detecting page type...")
page_type = detect_page_type(html_content, url, content_type)
print(f"   ✅ Page type: {page_type}\n")

# 4. Extract
print("4. Extracting with improved prompt...")
extractor = PropertyExtractor()
result = extractor.extract(
    url=url,
    html_content=html_content,
    content_type='local_tips',
    page_type='general'
)
print(f"   ✅ Extraction confidence: {result.get('extraction_confidence')}\n")

# 5. Check destinations
field_confidence = result.get('field_confidence', {})
destinations = field_confidence.get('destinations_covered', [])

print(f"📍 DESTINOS EXTRAÍDOS: {len(destinations)} total\n")

if len(destinations) >= 8:
    print("✅ SUCCESS! Extrajo 8+ destinos como se requería\n")
else:
    print(f"⚠️  WARNING: Solo extrajo {len(destinations)} destinos (se requieren 8-12)\n")

for i, dest in enumerate(destinations, 1):
    name = dest.get('name', 'Unknown')
    best_for = dest.get('best_for', 'N/A')
    highlights = dest.get('highlights', [])
    activities = dest.get('activities', [])
    
    print(f"{i}. {name} ({best_for})")
    print(f"   Highlights: {highlights[:3]}")
    print(f"   Activities: {activities[:3]}")
    print()

# 6. Save to database
print("\n6. Saving to database...")
property_obj = Property.objects.create(
    source_url=url,
    content_type='local_tips',
    page_type='general',
    extraction_confidence=result.get('extraction_confidence', 0.0),
    field_confidence=field_confidence
)

local_tip = LocalTipsGeneral.objects.create(
    base_property=property_obj,
    title=result.get('title', ''),
    description=result.get('description', ''),
    category=result.get('category', 'general'),
    practical_advice=result.get('practical_advice', []),
    location=result.get('location', ''),
    cost_estimate=result.get('cost_estimate'),
    best_time=result.get('best_time'),
    things_to_avoid=result.get('things_to_avoid', []),
    local_customs=result.get('local_customs', []),
    emergency_contacts=result.get('emergency_contacts', [])
)

print(f"✅ Saved LocalTipsGeneral ID: {local_tip.id}")
print(f"\n🎯 RESULTADO FINAL:")
print(f"   - Destinos extraídos: {len(destinations)}")
print(f"   - Objetivo: 8-12 destinos")
print(f"   - Status: {'✅ PASS' if len(destinations) >= 8 else '❌ FAIL'}")
