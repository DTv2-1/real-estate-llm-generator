#!/usr/bin/env python
"""
Test completo de extracción de datos de restaurante.
Verifica que se extraigan todos los campos disponibles del HTML.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from core.scraping.scraper import WebScraper
from core.llm.extraction import PropertyExtractor


async def test_restaurant_extraction():
    """Test de extracción de restaurante Amana."""
    
    url = "https://www.tripadvisor.com/Restaurant_Review-g309293-d26501860-Reviews-Amana-San_Jose_San_Jose_Metro_Province_of_San_Jose.html"
    
    print("=" * 80)
    print("🧪 TEST: Extracción de datos de Restaurante Amana")
    print("=" * 80)
    print(f"URL: {url}\n")
    
    # Paso 1: Scraping
    print("📥 PASO 1: Scraping HTML...")
    scraper = WebScraper()
    result = await scraper.scrape(url)
    
    if not result['success']:
        print(f"❌ Error en scraping: {result.get('error')}")
        return
    
    html = result['html']
    print(f"✅ HTML descargado: {len(html):,} caracteres\n")
    
    # Paso 2: Extracción
    print("🤖 PASO 2: Extracción con LLM...")
    extractor = PropertyExtractor(
        content_type='restaurant',
        page_type='specific'
    )
    
    data = extractor.extract_from_html(html, url=url)
    
    print("\n" + "=" * 80)
    print("📊 RESULTADOS DE EXTRACCIÓN")
    print("=" * 80)
    
    # Campos básicos
    print(f"\n🏪 INFORMACIÓN BÁSICA:")
    print(f"  • Nombre: {data.get('property_name')}")
    print(f"  • Tipo de cocina: {data.get('property_type')}")
    print(f"  • Rango de precio: {data.get('price_range')}")
    print(f"  • Rating: {data.get('rating')}")
    print(f"  • Número de reviews: {data.get('number_of_reviews')}")
    print(f"  • Ubicación: {data.get('location')}")
    print(f"  • Teléfono: {data.get('contact_phone')}")
    
    # Descripción
    print(f"\n📝 DESCRIPCIÓN:")
    desc = data.get('description')
    if desc:
        print(f"  {desc[:300]}{'...' if len(desc) > 300 else ''}")
    else:
        print("  ❌ No extraída")
    
    # Platos destacados
    print(f"\n⭐ PLATOS DESTACADOS:")
    dishes = data.get('signature_dishes')
    if dishes:
        if isinstance(dishes, list):
            for dish in dishes[:10]:
                print(f"  • {dish}")
            if len(dishes) > 10:
                print(f"  ... y {len(dishes) - 10} más")
        else:
            print(f"  {dishes}")
    else:
        print("  ❌ No extraídos")
    
    # Amenidades
    print(f"\n✨ AMENIDADES:")
    amenities = data.get('amenities')
    if amenities and len(amenities) > 0:
        for amenity in amenities[:15]:
            print(f"  • {amenity}")
        if len(amenities) > 15:
            print(f"  ... y {len(amenities) - 15} más")
    else:
        print("  ❌ No extraídas")
    
    # Horarios
    print(f"\n🕐 HORARIOS:")
    hours = data.get('opening_hours')
    if hours:
        if isinstance(hours, dict):
            for day, time in hours.items():
                if isinstance(time, list):
                    print(f"  • {day}: {', '.join(time)}")
                else:
                    print(f"  • {day}: {time}")
        else:
            print(f"  {hours}")
    else:
        print("  ❌ No extraídos")
    
    # Experiencias especiales
    print(f"\n✨ EXPERIENCIAS ESPECIALES:")
    special = data.get('special_experiences')
    if special:
        print(f"  {special}")
    else:
        print("  ❌ No extraídas")
    
    # Opciones dietéticas
    print(f"\n🥗 OPCIONES DIETÉTICAS:")
    dietary = data.get('dietary_options')
    if dietary and len(dietary) > 0:
        for option in dietary:
            print(f"  • {option}")
    else:
        print("  ❌ No extraídas")
    
    # Ambiente
    print(f"\n🎭 AMBIENTE:")
    atmosphere = data.get('atmosphere')
    if atmosphere:
        print(f"  {atmosphere}")
    else:
        print("  ❌ No extraído")
    
    # Detalles de precios
    print(f"\n💰 DETALLES DE PRECIOS:")
    price_details = data.get('price_details')
    if price_details and any(price_details.values()):
        for key, value in price_details.items():
            if value:
                print(f"  • {key}: {value}")
    else:
        print("  ❌ No extraídos del HTML")
    
    # Análisis de fuentes de extracción
    print(f"\n" + "=" * 80)
    print("📊 ANÁLISIS DE FUENTES DE EXTRACCIÓN")
    print("=" * 80)
    
    # Guardar datos antes de web search para comparar
    html_only_fields = {}
    web_search_fields = {}
    
    important_fields = [
        'property_name', 'property_type', 'price_range', 'location', 
        'description', 'signature_dishes', 'amenities', 'opening_hours',
        'special_experiences', 'dietary_options', 'atmosphere', 'rating',
        'number_of_reviews', 'contact_phone', 'reservation_required', 'price_details'
    ]
    
    # Identificar qué campos vienen del HTML vs Web Search
    # Los campos en field_confidence vienen de la extracción HTML original
    field_confidence = data.get('field_confidence', {})
    
    for field in important_fields:
        value = data.get(field)
        
        # Si el campo tiene valor
        if value and value != [] and value != {} and value != '':
            # Si está en field_confidence con evidencia, viene del HTML
            if field in field_confidence and field_confidence[field]:
                html_only_fields[field] = value
            else:
                # Si no tiene evidencia pero tiene valor, viene de web search o inferencia
                web_search_fields[field] = value
    
    # Verificar si se realizó web search
    web_context = data.get('web_search_context')
    web_search_performed = web_context and len(web_context) > 0
    
    print(f"\n✅ CAMPOS EXTRAÍDOS DEL HTML (OpenAI gpt-4o-mini):")
    if html_only_fields:
        for field, value in html_only_fields.items():
            if isinstance(value, list):
                print(f"  • {field}: {len(value)} items")
            elif isinstance(value, dict):
                print(f"  • {field}: {len(value)} keys")
            elif isinstance(value, str) and len(value) > 50:
                print(f"  • {field}: {value[:50]}...")
            else:
                print(f"  • {field}: {value}")
    else:
        print("  ⚠️ Ninguno (problema de extracción)")
    
    print(f"\n🌐 CAMPOS OBTENIDOS VÍA WEB SEARCH (OpenAI gpt-4o):")
    if web_search_performed:
        print(f"  ✅ Web search realizado ({len(web_context):,} caracteres)")
        print(f"  Fuentes: {len(data.get('web_search_sources', []))} URLs")
        if web_search_fields:
            for field, value in web_search_fields.items():
                if isinstance(value, list):
                    print(f"  • {field}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"  • {field}: {len(value)} keys")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  • {field}: {value[:50]}...")
                else:
                    print(f"  • {field}: {value}")
        else:
            print("  ⚠️ Web search se realizó pero no agregó nuevos campos")
    else:
        print("  ⚠️ No se realizó web search (todos los campos críticos llenos desde HTML)")
    
    # Confianza
    print(f"\n📈 CONFIANZA:")
    print(f"  • Confianza de extracción: {data.get('extraction_confidence', 0):.2f}")
    
    # Resumen de campos extraídos
    print(f"\n📊 RESUMEN TOTAL:")
    total_fields = len(important_fields)
    filled_fields = len(html_only_fields) + len(web_search_fields)
    
    percentage = (filled_fields / total_fields * 100) if total_fields > 0 else 0
    print(f"  • Campos extraídos del HTML: {len(html_only_fields)}/{total_fields}")
    print(f"  • Campos agregados por Web Search: {len(web_search_fields)}/{total_fields}")
    print(f"  • TOTAL completado: {filled_fields}/{total_fields} ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
    
    # Guardar JSON para inspección
    output_file = Path(__file__).parent / 'restaurant_extraction_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 Datos guardados en: {output_file}")


if __name__ == '__main__':
    asyncio.run(test_restaurant_extraction())
