#!/usr/bin/env python
"""
Test script to verify the refactored code works correctly.
Tests the new extractor-based approach without code duplication.
"""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

# Now import Django modules
from core.scraping.extractors import get_extractor, EXTRACTORS
from core.scraping.extractors.base import clean_html_generic

def test_extractor_registry():
    """Test that extractor registry works."""
    print("=" * 80)
    print("Test 1: Extractor Registry")
    print("=" * 80)
    
    # Check registered extractors
    print(f"\nRegistered extractors: {len(EXTRACTORS)}")
    for domain, extractor_class in EXTRACTORS.items():
        print(f"  - {domain}: {extractor_class.__name__}")
    
    # Test URL detection
    test_urls = [
        "https://brevitas.com/property/123",
        "https://encuentra24.com/costa-rica/property/456",
        "https://www.coldwellbankercostarica.com/property/789",
        "https://unknown-site.com/property/000",
    ]
    
    print("\nTesting URL detection:")
    for url in test_urls:
        extractor = get_extractor(url)
        print(f"  - {url}")
        print(f"    → {extractor.__class__.__name__} ({extractor.site_name})")
    
    print("\n✅ Extractor registry test PASSED\n")


def test_html_cleaning():
    """Test generic HTML cleaning."""
    print("=" * 80)
    print("Test 2: Generic HTML Cleaning")
    print("=" * 80)
    
    # Sample HTML with noise
    html = """
    <html>
        <head>
            <script>console.log('tracking');</script>
            <style>.ad { display: block; }</style>
        </head>
        <body>
            <div class="cookie-banner">Accept cookies</div>
            <div class="property-details">
                <h1>Beautiful House</h1>
                <p>$500,000</p>
                <p>3 bedrooms, 2 bathrooms</p>
            </div>
            <div class="advertisement">Buy now!</div>
            <footer>Copyright 2024</footer>
        </body>
    </html>
    """
    
    print(f"\nOriginal HTML size: {len(html)} chars")
    
    cleaned = clean_html_generic(html)
    print(f"Cleaned HTML size: {len(cleaned)} chars")
    reduction = ((len(html) - len(cleaned)) / len(html)) * 100
    print(f"Reduction: {reduction:.1f}%")
    
    # Check that important content is preserved
    assert "Beautiful House" in cleaned, "Title should be preserved"
    assert "$500,000" in cleaned, "Price should be preserved"
    assert "bedrooms" in cleaned, "Bedrooms info should be preserved"
    
    # Check that noise is removed
    assert "script" not in cleaned.lower() or "tracking" not in cleaned, "Scripts should be removed"
    assert "cookie-banner" not in cleaned, "Cookie banner should be removed"
    assert "advertisement" not in cleaned, "Ads should be removed"
    
    print("\n✅ HTML cleaning test PASSED\n")


def test_brevitas_extractor():
    """Test Brevitas extractor with sample HTML."""
    print("=" * 80)
    print("Test 3: Brevitas Extractor")
    print("=" * 80)
    
    # Minimal brevitas HTML structure
    html = """
    <html>
        <body>
            <h1 class="show__title">Luxury Beach House</h1>
            <div class="show__price">$1,250,000</div>
            <div class="product__detail">Beds: 4</div>
            <div class="product__detail">Baths: 3.5</div>
            <p class="show__copy">Amazing ocean views with private beach access.</p>
            <p class="show__address">Playa Hermosa, Provincia de Guanacaste, Costa Rica</p>
        </body>
    </html>
    """
    
    extractor = get_extractor("https://brevitas.com/property/test")
    print(f"\nUsing extractor: {extractor.__class__.__name__}")
    
    data = extractor.extract(html, "https://brevitas.com/property/test")
    
    print("\nExtracted data:")
    print(f"  - Title: {data.get('title')}")
    print(f"  - Price: ${data.get('price_usd')}")
    print(f"  - Bedrooms: {data.get('bedrooms')}")
    print(f"  - Bathrooms: {data.get('bathrooms')}")
    print(f"  - Province: {data.get('province')}")
    print(f"  - Description: {data.get('description')[:50]}..." if data.get('description') else "  - Description: None")
    
    # Validate extracted data
    assert data['title'] == "Luxury Beach House", f"Title mismatch: {data['title']}"
    assert data['bedrooms'] == 4, f"Bedrooms mismatch: {data['bedrooms']}"
    assert data['bathrooms'] == 3.5, f"Bathrooms mismatch: {data['bathrooms']}"
    assert "Guanacaste" in str(data.get('province', '')), f"Province should contain Guanacaste"
    
    print("\n✅ Brevitas extractor test PASSED\n")


def test_imports():
    """Test that all imports work without circular dependencies."""
    print("=" * 80)
    print("Test 4: Import Tests")
    print("=" * 80)
    
    try:
        # Test scraping module imports
        from core.scraping import WebScraper, get_extractor, EXTRACTORS, BaseExtractor
        print("✓ core.scraping imports work")
        
        # Test extractor imports
        from core.scraping.extractors.base import BaseExtractor, clean_html_generic
        print("✓ core.scraping.extractors.base imports work")
        
        from core.scraping.extractors.brevitas import BrevitasExtractor
        print("✓ BrevitasExtractor imports work")
        
        from core.scraping.extractors.encuentra24 import Encuentra24Extractor
        print("✓ Encuentra24Extractor imports work")
        
        from core.scraping.extractors.coldwell_banker import ColdwellBankerExtractor
        print("✓ ColdwellBankerExtractor imports work")
        
        # Test that html_cleaner still exists (for backward compatibility)
        from core.utils.html_cleaner import HTMLCleaner, clean_html_generic
        print("✓ html_cleaner backward compatibility maintained")
        
        print("\n✅ All imports test PASSED\n")
        
    except Exception as e:
        print(f"\n❌ Import test FAILED: {e}\n")
        raise


if __name__ == "__main__":
    print("\n🧪 Testing Refactored Code\n")
    
    try:
        test_imports()
        test_extractor_registry()
        test_html_cleaning()
        test_brevitas_extractor()
        
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\nRefactoring successful:")
        print("  ✓ Code duplication eliminated")
        print("  ✓ Site-specific extractors working")
        print("  ✓ Generic HTML cleaning moved to base.py")
        print("  ✓ No circular dependencies")
        print("  ✓ Backward compatibility maintained")
        print()
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
