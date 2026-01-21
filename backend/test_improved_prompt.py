#!/usr/bin/env python3
"""Test extraction with improved prompt."""
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

import requests
import json

print("🔄 Testing improved prompt with WikiVoyage Costa Rica...\n")

response = requests.post(
    'http://localhost:8000/api/data-collector/extract/',
    json={'url': 'https://en.wikivoyage.org/wiki/Costa_Rica'},
    timeout=300
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Extraction completed!")
    print(f"Content Type: {data.get('content_type')}")
    print(f"Confidence: {data.get('extraction_confidence')}\n")
    
    if 'destinations_covered' in data:
        dests = data['destinations_covered']
        print(f"📍 DESTINOS EXTRAÍDOS: {len(dests)} total\n")
        
        for i, dest in enumerate(dests, 1):
            name = dest.get('name', 'Unknown')
            best_for = dest.get('best_for', 'N/A')
            highlights = dest.get('highlights', [])
            
            print(f"{i}. {name} ({best_for})")
            if highlights:
                preview = highlights[:2] if len(highlights) > 2 else highlights
                print(f"   Highlights: {preview}")
            print()
    else:
        print("❌ No destinations_covered field found")
        print(f"Available fields: {list(data.keys())[:15]}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text[:500])
