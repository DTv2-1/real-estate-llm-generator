"""
Comparar GPT-4o-mini vs GPT-4o para extracción de propiedades de Encuentra24
"""

import sys
import os
import django
import json
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.scraping.scraper import scrape_url
from core.scraping.extractors.encuentra24 import Encuentra24Extractor
import openai
from django.conf import settings

# URL de prueba
TEST_URL = "https://www.encuentra24.com/costa-rica-es/bienes-raices-venta-de-propiedades-negocios/organica-yoga-retreat-vista-inigualable-a-isla-tortuga/31786735"

print("=" * 80)
print("🔬 COMPARACIÓN GPT-4o-mini vs GPT-4o")
print("=" * 80)
print(f"URL: {TEST_URL}\n")

# Scrape la página
print("📥 Scrapeando página...")
scrape_result = scrape_url(TEST_URL)
html = scrape_result['html']
print(f"✅ HTML obtenido: {len(html)} caracteres\n")

# Crear extractor
extractor = Encuentra24Extractor()
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Extraer texto limpio
full_text = extractor.extract_all_text(soup)
construction_stage = extractor.extract_construction_stage(soup)

print(f"📝 Texto limpio: {len(full_text)} caracteres")
print(f"🏗️ Construction stage: {construction_stage}\n")

# Contexto para la AI
context = f"""Texto de la propiedad:
{full_text}

Etapa de construcción: {construction_stage or 'No disponible'}
"""

# Guardar archivo de prueba
with open('ai_input_text_test.txt', 'w', encoding='utf-8') as f:
    f.write(context)

print("💾 Contexto guardado en: ai_input_text_test.txt\n")

# Prompt
prompt = """Analyze the real estate property information and extract/normalize the following fields in JSON format:

{
  "title": "Property name or descriptive title (max 100 chars)",
  "price_usd": <numeric price in USD>,
  "bedrooms": <number or null>,
  "bathrooms": <number or null>,
  "area_m2": <number or null>,
  "lot_size_m2": <number or null>,
  "property_type": "Casa|Apartamento|Terreno|Lote|Condominio|etc",
  "listing_type": "sale|rent",
  "location": "City, Province, Country",
  "amenities": ["amenity1", "amenity2", ...],
  "parking_spaces": <number or null>,
  "pool": <boolean>,
  "description": "Professional property description (2-3 sentences, max 500 chars)"
}

CRITICAL INSTRUCTIONS:

TITLE:
- Extract the actual property/project NAME from the description
- Keep it concise and descriptive (max 100 chars)

DESCRIPTION:
- Write a professional, concise summary highlighting key selling points
- 2-3 sentences maximum (around 300-500 characters)

PRICE:
- Extract the REAL sale/rent price (NOT price per m²)
- Format "1,640,000" → convert to 1640000

LISTING TYPE:
- If URL contains "venta" or text mentions sale → "sale"
- If URL contains "alquiler" or text mentions rent → "rent"

AREA:
- Extract area in m² (NOT price per m²)
- "m² 400" → 400
- "Precio/M² de construcción $4,100" is PRICE PER SQM, not area

PARKING:
- Extract number from "Parking 3" → 3
"""

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def test_model(model_name):
    """Test un modelo específico"""
    print(f"\n{'=' * 80}")
    print(f"🤖 Probando modelo: {model_name}")
    print(f"{'=' * 80}\n")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a real estate data extraction expert. Extract and normalize property information accurately. Always return valid JSON."},
                {"role": "user", "content": f"{prompt}\n\n{context}"}
            ],
            temperature=0,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Tokens usados
        usage = response.usage
        print(f"📊 Tokens usados:")
        print(f"   - Prompt: {usage.prompt_tokens}")
        print(f"   - Completion: {usage.completion_tokens}")
        print(f"   - Total: {usage.total_tokens}\n")
        
        # Mostrar resultado formateado
        print("📋 Resultado extraído:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result, usage
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

# Probar ambos modelos
print("\n" + "🔵" * 40)
print("MODELO 1: GPT-4o-mini (actual)")
print("🔵" * 40)
result_mini, usage_mini = test_model("gpt-4o-mini")

print("\n" + "🟢" * 40)
print("MODELO 2: GPT-4o (más potente)")
print("🟢" * 40)
result_4o, usage_4o = test_model("gpt-4o")

# Comparar resultados
print("\n" + "=" * 80)
print("📊 COMPARACIÓN DE RESULTADOS")
print("=" * 80)

if result_mini and result_4o:
    fields = ['title', 'price_usd', 'bedrooms', 'bathrooms', 'area_m2', 'lot_size_m2', 
              'property_type', 'listing_type', 'location', 'parking_spaces', 'pool']
    
    print(f"\n{'Campo':<20} {'GPT-4o-mini':<30} {'GPT-4o':<30} {'Match?':<10}")
    print("-" * 100)
    
    for field in fields:
        val_mini = result_mini.get(field, 'N/A')
        val_4o = result_4o.get(field, 'N/A')
        match = "✅" if val_mini == val_4o else "❌"
        print(f"{field:<20} {str(val_mini):<30} {str(val_4o):<30} {match:<10}")
    
    # Costos aproximados (precios de OpenAI)
    print("\n" + "=" * 80)
    print("💰 COSTOS APROXIMADOS (USD)")
    print("=" * 80)
    
    # Precios por 1M tokens (aproximados)
    MINI_INPUT_COST = 0.150 / 1_000_000  # $0.150 per 1M input tokens
    MINI_OUTPUT_COST = 0.600 / 1_000_000  # $0.600 per 1M output tokens
    GPT4O_INPUT_COST = 2.50 / 1_000_000   # $2.50 per 1M input tokens
    GPT4O_OUTPUT_COST = 10.00 / 1_000_000  # $10.00 per 1M output tokens
    
    if usage_mini:
        cost_mini = (usage_mini.prompt_tokens * MINI_INPUT_COST) + (usage_mini.completion_tokens * MINI_OUTPUT_COST)
        print(f"\nGPT-4o-mini:")
        print(f"  - Por request: ${cost_mini:.6f}")
        print(f"  - Por 1,000 propiedades: ${cost_mini * 1000:.2f}")
    
    if usage_4o:
        cost_4o = (usage_4o.prompt_tokens * GPT4O_INPUT_COST) + (usage_4o.completion_tokens * GPT4O_OUTPUT_COST)
        print(f"\nGPT-4o:")
        print(f"  - Por request: ${cost_4o:.6f}")
        print(f"  - Por 1,000 propiedades: ${cost_4o * 1000:.2f}")
    
    if usage_mini and usage_4o:
        diff = cost_4o - cost_mini
        print(f"\nDiferencia por propiedad: ${diff:.6f}")
        print(f"Diferencia por 1,000 propiedades: ${diff * 1000:.2f}")
        print(f"GPT-4o es {cost_4o / cost_mini:.1f}x más caro")

print("\n" + "=" * 80)
print("✅ Comparación completa")
print("=" * 80)
