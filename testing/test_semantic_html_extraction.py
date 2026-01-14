#!/usr/bin/env python
"""Test semantic HTML extraction with AI."""

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

def test_semantic_extraction():
    """Test the semantic HTML + AI extractor."""
    
    # Test URL
    test_url = "https://www.encuentra24.com/costa-rica-es/bienes-raices-venta-de-propiedades-negocios/organica-yoga-retreat-vista-inigualable-a-isla-tortuga/31786735"
    
    print("=" * 80)
    print("🧪 PRUEBA: HTML SEMÁNTICO + AI")
    print("=" * 80)
    print(f"URL: {test_url}\n")
    
    # Step 1: Scrape
    print("📥 Scrapeando página...")
    result = scrape_url(test_url)
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('error')}")
        return
    
    html = result.get('html', '')
    print(f"✅ HTML obtenido: {len(html):,} caracteres\n")
    
    # Step 2: Extract with semantic HTML method
    print("🔍 Extrayendo con HTML semántico + AI...")
    print("-" * 80)
    
    extractor = Encuentra24Extractor()
    data = extractor.extract(html, test_url)
    
    print("-" * 80)
    print("\n📋 DATOS EXTRAÍDOS:")
    print("=" * 80)
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
    print("=" * 80)
    
    # Validation
    print("\n✅ VALIDACIÓN:")
    print("-" * 80)
    
    checks = [
        ("title", data.get('title'), "debe existir"),
        ("parking_spaces", data.get('parking_spaces'), "debe ser 3 (o al menos existir)"),
        ("area_m2", data.get('area_m2'), "debe ser ~400 (NO 4100)"),
        ("listing_type", data.get('listing_type'), "debe ser 'sale'"),
        ("location", data.get('location'), "debe tener ciudad/provincia"),
        ("property_type", data.get('property_type'), "debe existir (Casa, etc)"),
        ("pool", data.get('pool'), "debe existir (true/false)"),
    ]
    
    passed = 0
    failed = 0
    
    for field, value, expectation in checks:
        if value:
            print(f"✅ {field}: {value}")
            passed += 1
        else:
            print(f"❌ {field}: {value} - {expectation}")
            failed += 1
    
    # Special checks
    if data.get('area_m2'):
        area = float(data['area_m2']) if data['area_m2'] else 0
        if 350 <= area <= 450:
            print(f"✅ area_m2 en rango correcto: {area} m²")
            passed += 1
        else:
            print(f"⚠️ area_m2 fuera de rango: {area} (esperado ~400)")
            failed += 1
    
    print("-" * 80)
    print(f"\n📊 RESUMEN: {passed} ✅ | {failed} ❌")
    
    if failed == 0:
        print("🎉 ¡PERFECTO! Todos los campos extraídos correctamente")
    elif failed <= 2:
        print("👍 Bueno, solo algunos campos faltantes")
    else:
        print(f"⚠️ {failed} validaciones fallaron")
    
    print("=" * 80)
    
    # Show cost estimate
    print("\n💰 ESTIMACIÓN DE COSTO:")
    print("-" * 80)
    print(f"Tokens estimados: ~600-800 por propiedad")
    print(f"Costo por propiedad: ~$0.0002")
    print(f"Costo por 1,000 propiedades: ~$0.20")
    print(f"Reducción vs método anterior: ~33%")
    print("=" * 80)

if __name__ == "__main__":
    test_semantic_extraction()
