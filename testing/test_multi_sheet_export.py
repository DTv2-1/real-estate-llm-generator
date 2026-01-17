#!/usr/bin/env python
"""
Test Multi-Sheet Export System
Tests the dynamic column generation for different content types and page types.
"""

import json
import requests
from typing import List, Dict

# Test Google Sheets URLs
TOUR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1sBJvL_UIDULvZeycsm-PPk0V3_LEXM9fIrWh5osQVCc/edit?gid=0#gid=0"
REAL_ESTATE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HU5yC3NDjx5xdQzsOCXejZLt7I2Mhb8iVw6z3dMMnTA/edit?gid=0#gid=0"

# Test URLs
TEST_URLS = [
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-curridabat/2785",
    "https://costarica.org/tours/"
]

API_BASE = "http://localhost:8000"


def extract_sheet_id(url: str) -> str:
    """Extract spreadsheet ID from Google Sheets URL."""
    import re
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else url


def process_url(url: str) -> Dict:
    """Process a single URL and return extracted data."""
    print(f"\n🔄 Procesando: {url}")
    
    try:
        response = requests.post(
            f"{API_BASE}/ingest/url/",
            json={"url": url},
            timeout=120
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Response: {response.text[:1000]}")
            return None
        
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Keys in response: {list(data.keys())}")
        
        # Check for 'status': 'success' format (new API)
        if data.get('status') == 'success':
            result = data.get('property', {})
            if not result:
                print(f"❌ No hay 'property' en la respuesta")
                return None
            
            # Add metadata to result
            result['content_type'] = data.get('content_type', 'unknown')
            result['page_type'] = data.get('page_type', 'unknown')
            result['url'] = url
            
            content_type = result.get('content_type', 'unknown')
            page_type = result.get('page_type', 'unknown')
            
            print(f"✅ Extraído: {content_type} ({page_type})")
            print(f"   Fields: {list(result.keys())[:10]}")
            
            return result
        
        # Check for old 'success': true format
        if not data.get('success'):
            print(f"❌ Extracción falló")
            print(f"   Error: {data.get('error')}")
            print(f"   Message: {data.get('message')}")
            return None
        
        result = data.get('result', {})
        if not result:
            print(f"❌ No hay resultado en la respuesta")
            print(f"   Full data: {json.dumps(data, indent=2)}")
            return None
        
        content_type = result.get('content_type', 'unknown')
        page_type = result.get('page_type', 'unknown')
        
        print(f"✅ Extraído: {content_type} ({page_type})")
        print(f"   Fields: {list(result.keys())[:10]}")
        
        return result
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout después de 120 segundos")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None


def export_to_sheets(results_by_type: Dict[str, List[Dict]]):
    """Export results grouped by content_type to their respective sheets."""
    print("\n" + "="*80)
    print("📤 EXPORTANDO A GOOGLE SHEETS")
    print("="*80)
    
    sheet_urls = {
        'tour': TOUR_SHEET_URL,
        'real_estate': REAL_ESTATE_SHEET_URL
    }
    
    for content_type, results in results_by_type.items():
        if not results:
            continue
        
        sheet_url = sheet_urls.get(content_type)
        if not sheet_url:
            print(f"⚠️ No hay sheet URL configurada para tipo: {content_type}")
            continue
        
        sheet_id = extract_sheet_id(sheet_url)
        print(f"\n📊 Exportando {len(results)} items de tipo '{content_type}'")
        print(f"   Sheet ID: {sheet_id}")
        
        # Get page_type from first result
        page_type = results[0].get('page_type', 'specific')
        print(f"   Page Type: {page_type}")
        
        # Export
        response = requests.post(
            f"{API_BASE}/ingest/batch-export/sheets/",
            json={
                "sheet_id": sheet_id,
                "results": results,
                "content_type": content_type
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Exportado exitosamente!")
            print(f"   Columnas creadas: {data.get('columns', [])}")
            print(f"   Items exportados: {data.get('exported_count', 0)}")
        else:
            print(f"❌ Error en exportación: {response.status_code}")
            print(f"   {response.text}")


def main():
    print("="*80)
    print("🧪 TEST: MULTI-SHEET EXPORT SYSTEM")
    print("="*80)
    print(f"\n📋 URLs a procesar:")
    for url in TEST_URLS:
        print(f"   - {url}")
    
    print(f"\n📊 Sheets configurados:")
    print(f"   🗺️  Tours: {TOUR_SHEET_URL}")
    print(f"   🏠 Real Estate: {REAL_ESTATE_SHEET_URL}")
    
    # Process URLs
    print("\n" + "="*80)
    print("🔄 PROCESANDO URLs")
    print("="*80)
    
    results_by_type = {}
    
    for url in TEST_URLS:
        result = process_url(url)
        if result:
            content_type = result.get('content_type', 'unknown')
            if content_type not in results_by_type:
                results_by_type[content_type] = []
            results_by_type[content_type].append(result)
    
    # Show results summary
    print("\n" + "="*80)
    print("📊 RESUMEN DE EXTRACCIÓN")
    print("="*80)
    
    for content_type, results in results_by_type.items():
        print(f"\n{content_type.upper()}: {len(results)} items")
        for i, result in enumerate(results, 1):
            page_type = result.get('page_type', 'unknown')
            title = result.get('title') or result.get('tour_name') or result.get('destination', 'Sin título')
            print(f"   {i}. [{page_type}] {title[:60]}")
    
    # Export to sheets
    if results_by_type:
        export_to_sheets(results_by_type)
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETADO")
    print("="*80)
    print("\nRevisa los Google Sheets para verificar las columnas:")
    print(f"   🗺️  Tours: {TOUR_SHEET_URL}")
    print(f"   🏠 Real Estate: {REAL_ESTATE_SHEET_URL}")


if __name__ == '__main__':
    main()
