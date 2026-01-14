#!/usr/bin/env python
"""Test optimized Encuentra24 extractor with structured HTML extraction."""

import sys
import os
import django

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from core.scraping.scraper import scrape_url
from core.scraping.extractors.encuentra24 import Encuentra24Extractor
import json

def test_optimized_extraction():
    """Test the optimized extractor on a known URL."""
    
    # Test URL with known issues
    test_url = "https://www.encuentra24.com/costa-rica-es/bienes-raices-venta-de-propiedades-negocios/organica-yoga-retreat-vista-inigualable-a-isla-tortuga/31786735"
    
    print("=" * 80)
    print("🧪 PRUEBA DE EXTRACTOR OPTIMIZADO")
    print("=" * 80)
    print(f"URL: {test_url}\n")
    
    # Step 1: Scrape the page
    print("📥 Scrapeando página...")
    result = scrape_url(test_url)
    
    if not result.get('success'):
        print(f"❌ Error scraping: {result.get('error')}")
        return
    
    html = result.get('html', '')
    print(f"✅ HTML obtenido: {len(html)} caracteres\n")
    
    # Step 2: Extract data using optimized extractor
    print("🔍 Extrayendo datos con extractor optimizado...")
    print("-" * 80)
    
    extractor = Encuentra24Extractor()
    extracted_data = extractor.extract(html, test_url)
    
    print("-" * 80)
    print("\n📋 DATOS EXTRAÍDOS:")
    print("=" * 80)
    print(json.dumps(extracted_data, indent=2, default=str, ensure_ascii=False))
    print("=" * 80)
    
    # Validation checks
    print("\n✅ VALIDACIÓN:")
    print("-" * 80)
    
    checks = {
        "parking_spaces": (extracted_data.get('parking_spaces'), 3, "Parking debe ser 3"),
        "area_m2": (extracted_data.get('area_m2'), 400, "Área debe ser 400 m²"),
        "listing_type": (extracted_data.get('listing_type'), "sale", "Tipo debe ser 'sale'"),
        "title": (bool(extracted_data.get('title')), True, "Título debe existir"),
        "location": (bool(extracted_data.get('location')), True, "Ubicación debe existir"),
    }
    
    passed = 0
    failed = 0
    
    for field, (actual, expected, message) in checks.items():
        if actual == expected:
            print(f"✅ {field}: {actual} (correcto)")
            passed += 1
        else:
            print(f"❌ {field}: {actual} (esperado: {expected}) - {message}")
            failed += 1
    
    print("-" * 80)
    print(f"\n📊 RESUMEN: {passed} pasadas, {failed} fallidas")
    
    if failed == 0:
        print("🎉 ¡TODAS LAS VALIDACIONES PASARON!")
    else:
        print(f"⚠️ {failed} validaciones fallaron")
    
    print("=" * 80)

if __name__ == "__main__":
    test_optimized_extraction()
