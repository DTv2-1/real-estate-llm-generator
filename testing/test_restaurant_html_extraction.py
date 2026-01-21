"""
Test para analizar qué HTML recibe el extractor y qué extrae
"""
import sys
import os
from pathlib import Path

# Cargar variables de entorno primero
from dotenv import load_dotenv
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
env_path = Path(backend_dir) / '.env'
load_dotenv(env_path)

# URL del restaurante Amana
url = "https://www.tripadvisor.com/Restaurant_Review-g309293-d26501860-Reviews-Amana-San_Jose_San_Jose_Metro_Province_of_San_Jose.html"

# Configurar Django antes de importar
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from core.scraping.scraper import WebScraper
from core.llm.extraction import PropertyExtractor

print("=" * 80)
print("🔍 TEST: Analizando HTML extraction para restaurante Amana")
print("=" * 80)
print(f"\n📍 URL: {url}\n")

# 1. Obtener HTML con Scrapfly
print("1️⃣ Obteniendo HTML con WebScraper...")
scraper = WebScraper()
result = scraper.scrape_sync(url)

if not result['success']:
    print(f"❌ Error al scrapear: {result.get('error')}")
    sys.exit(1)

html_content = result['html']
print(f"✅ HTML obtenido: {len(html_content)} caracteres")

# Guardar HTML completo
html_file = os.path.join(os.path.dirname(__file__), 'restaurant_html_full.txt')
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"💾 HTML completo guardado en: restaurant_html_full.txt")

# 2. Ver qué texto limpio extrae Scrapfly
print("\n2️⃣ Texto limpio extraído por Scrapfly:")
cleaned_text = result.get('text', '')
print(f"   Longitud: {len(cleaned_text)} caracteres")
print(f"   Primeros 500 chars:")
print("   " + "-" * 76)
print(f"   {cleaned_text[:500]}")
print("   " + "-" * 76)

# Guardar texto limpio
cleaned_file = os.path.join(os.path.dirname(__file__), 'restaurant_cleaned_text.txt')
with open(cleaned_file, 'w', encoding='utf-8') as f:
    f.write(cleaned_text)
print(f"💾 Texto limpio guardado en: restaurant_cleaned_text.txt")

# 3. Extraer con LLM (como lo hace el sistema)
print("\n3️⃣ Extrayendo datos con LLM...")
extractor = PropertyExtractor(content_type='restaurant', page_type='specific')
extraction_result = extractor.extract_from_html(html_content, url)

print(f"\n✅ Extracción completada!")
print(f"   Confianza: {extraction_result.get('extraction_confidence', 0)}")
print(f"\n📊 Campos extraídos del HTML:")
print("   " + "=" * 76)

# Contar campos no-null
extracted_fields = {}
null_fields = []

for key, value in extraction_result.items():
    if key.endswith('_evidence') or key in ['extraction_confidence', 'confidence_reasoning']:
        continue
    
    if value is not None and value != '' and value != {} and value != []:
        extracted_fields[key] = value
        print(f"   ✅ {key}: {str(value)[:100]}")
    else:
        null_fields.append(key)

print(f"\n   Total campos extraídos: {len(extracted_fields)}")
print(f"   Total campos null/vacíos: {len(null_fields)}")

# Guardar resultado de extracción
extraction_file = os.path.join(os.path.dirname(__file__), 'restaurant_extraction_result.txt')
with open(extraction_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("RESULTADO DE EXTRACCIÓN DEL HTML\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"URL: {url}\n")
    f.write(f"Confianza: {extraction_result.get('extraction_confidence', 0)}\n")
    f.write(f"Razonamiento: {extraction_result.get('confidence_reasoning', 'N/A')}\n\n")
    
    f.write("CAMPOS EXTRAÍDOS:\n")
    f.write("-" * 80 + "\n")
    for key, value in extracted_fields.items():
        f.write(f"\n{key}:\n{value}\n")
    
    f.write("\n\n")
    f.write("CAMPOS NULL/VACÍOS:\n")
    f.write("-" * 80 + "\n")
    for field in null_fields:
        f.write(f"  - {field}\n")

print(f"\n💾 Resultado completo guardado en: restaurant_extraction_result.txt")

print("\n" + "=" * 80)
print("📁 Archivos generados:")
print("   1. restaurant_html_full.txt - HTML completo de Scrapfly")
print("   2. restaurant_cleaned_text.txt - Texto limpio extraído")
print("   3. restaurant_extraction_result.txt - Resultado de LLM extraction")
print("=" * 80)
