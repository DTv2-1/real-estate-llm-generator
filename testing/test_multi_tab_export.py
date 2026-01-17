#!/usr/bin/env python
"""
Test Multi-Tab Export System
Tests automatic tab creation for specific vs general pages within same spreadsheet.
"""

import json
import requests
from typing import List, Dict

# Test Google Sheets URLs
TOUR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1sBJvL_UIDULvZeycsm-PPk0V3_LEXM9fIrWh5osQVCc/edit?gid=0#gid=0"
REAL_ESTATE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HU5yC3NDjx5xdQzsOCXejZLt7I2Mhb8iVw6z3dMMnTA/edit?gid=0#gid=0"

# Test URLs - Mixed specific and general
TEST_URLS = [
    # Real Estate - Specific
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-curridabat/2785",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-uvita/3899",
    
    # Tours - General
    "https://costarica.org/tours/",
    "https://costarica.org/tours/arenal/",
    
    # Tours - Specific (if we had them)
    # "https://www.desafiocostarica.com/tour-detail/rafting-balsa-river-costa-rica-2-3",
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
        
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get('status') == 'success':
            result = data.get('property', {})
            if not result:
                print(f"❌ No hay 'property' en la respuesta")
                return None
            
            # Add metadata to result
            result['content_type'] = data.get('content_type', 'unknown')
            result['page_type'] = data.get('page_type', 'unknown')
            result['source_url'] = url
            
            content_type = result.get('content_type', 'unknown')
            page_type = result.get('page_type', 'unknown')
            
            print(f"✅ Extraído: {content_type} ({page_type})")
            
            return result
        
        print(f"❌ Extracción falló")
        return None
        
    except requests.Timeout:
        print(f"⏱️  Timeout después de 120 segundos")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def export_to_sheets(content_type: str, results: List[Dict], sheet_url: str) -> bool:
    """Export results to Google Sheets with automatic tab creation."""
    sheet_id = extract_sheet_id(sheet_url)
    
    print(f"\n📊 Exportando {len(results)} items de tipo '{content_type}'")
    print(f"   Sheet ID: {sheet_id}")
    
    # Count page types
    page_types = {}
    for r in results:
        pt = r.get('page_type', 'unknown')
        page_types[pt] = page_types.get(pt, 0) + 1
    
    print(f"   Page Types: {page_types}")
    
    try:
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
            
            if 'tabs' in data:
                print(f"   📑 Tabs creados:")
                for tab in data['tabs']:
                    print(f"      - {tab['tab_name']}: {tab['items_count']} items, {tab['columns_count']} columnas")
            
            return True
        else:
            print(f"❌ Error en export: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error exportando: {e}")
        return False


def main():
    print("=" * 80)
    print("🧪 TEST: MULTI-TAB EXPORT SYSTEM")
    print("=" * 80)
    
    print(f"\n📋 URLs a procesar:")
    for url in TEST_URLS:
        print(f"   - {url}")
    
    print(f"\n📊 Sheets configurados:")
    print(f"   🗺️  Tours: {TOUR_SHEET_URL}")
    print(f"   🏠 Real Estate: {REAL_ESTATE_SHEET_URL}")
    
    # Process all URLs
    print("\n" + "=" * 80)
    print("🔄 PROCESANDO URLs")
    print("=" * 80)
    
    all_results = []
    for url in TEST_URLS:
        result = process_url(url)
        if result:
            all_results.append(result)
    
    # Group by content_type
    groups = {}
    for result in all_results:
        ct = result.get('content_type', 'unknown')
        if ct not in groups:
            groups[ct] = []
        groups[ct].append(result)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE EXTRACCIÓN")
    print("=" * 80)
    
    for content_type, items in groups.items():
        print(f"\n{content_type.upper()}: {len(items)} items")
        
        # Group by page_type for display
        page_groups = {}
        for item in items:
            pt = item.get('page_type', 'unknown')
            if pt not in page_groups:
                page_groups[pt] = []
            page_groups[pt].append(item)
        
        for page_type, page_items in page_groups.items():
            print(f"  [{page_type}]:")
            for item in page_items:
                title = item.get('title') or item.get('destination') or item.get('tour_name') or 'Sin título'
                print(f"   - {title[:60]}")
    
    # Export to Google Sheets
    print("\n" + "=" * 80)
    print("📤 EXPORTANDO A GOOGLE SHEETS (CON TABS AUTOMÁTICOS)")
    print("=" * 80)
    
    sheet_mapping = {
        'tour': TOUR_SHEET_URL,
        'real_estate': REAL_ESTATE_SHEET_URL
    }
    
    for content_type, items in groups.items():
        sheet_url = sheet_mapping.get(content_type)
        if not sheet_url:
            print(f"⚠️  No hay sheet configurado para {content_type}")
            continue
        
        export_to_sheets(content_type, items, sheet_url)
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
    
    print("\nRevisa los Google Sheets - deberías ver tabs separados:")
    print("   🗺️  Tours: Tabs 'Específicos' y 'Generales'")
    print(f"      {TOUR_SHEET_URL}")
    print("   🏠 Real Estate: Tabs 'Específicos' y 'Generales'")
    print(f"      {REAL_ESTATE_SHEET_URL}")


if __name__ == "__main__":
    main()
