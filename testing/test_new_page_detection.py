#!/usr/bin/env python
"""
Quick test for the new simplified page_type_detection.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django with proper environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load .env file
from dotenv import load_dotenv
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")
else:
    print(f"⚠️ No .env file found at {env_path}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.llm.page_type_detection import detect_page_type

def test_page_detection():
    """Test the new simplified page detection"""
    
    # Test URLs
    test_cases = [
        {
            "url": "https://panamatours.com/colon-city-and-panama-canal-tour/",
            "content_type": "tour",
            "expected": "specific"
        },
        {
            "url": "https://panamatours.com/tours/",
            "content_type": "tour",
            "expected": "general"
        },
        {
            "url": "https://www.encuentra24.com/panama-en/properties-for-sale",
            "content_type": "real_estate",
            "expected": "general"
        }
    ]
    
    print("\n" + "="*80)
    print("Testing New Simplified Page Type Detection (173 lines vs 840 lines)")
    print("="*80 + "\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {case['url']}")
        print(f"Expected: {case['expected']}")
        print("-" * 80)
        
        try:
            page_type, confidence, metadata = detect_page_type(
                url=case['url'],
                html_content="<html><body>Test content</body></html>",
                content_type=case['content_type']
            )
            
            print(f"✅ Result: {page_type} (confidence: {confidence:.2f})")
            print(f"   Method: {metadata.get('method', 'unknown')}")
            
            if 'web_search_answer' in metadata:
                print(f"   Web Search Answer: {metadata['web_search_answer'][:100]}...")
            
            if 'fallback_pattern' in metadata:
                print(f"   Fallback Pattern: {metadata['fallback_pattern']}")
            
            match = "✅ MATCH" if page_type == case['expected'] else "❌ MISMATCH"
            print(f"\n{match}\n")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
    
    print("="*80)
    print("Test completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_page_detection()
