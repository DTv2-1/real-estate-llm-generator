#!/usr/bin/env python
"""
Test Google Sheets Auto-Tab Creation

Tests the /ingest/google-sheet/ endpoint with URL classification
and automatic tab creation using the format: content_type_page_type
"""

import requests
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_google_sheets_auto_tabs():
    """Test Google Sheets with automatic tab creation"""
    
    print("=" * 80)
    print("🧪 TEST: GOOGLE SHEETS AUTO-TAB CREATION")
    print("=" * 80)
    
    # API endpoint
    api_url = "http://localhost:8000/ingest/google-sheet/"
    
    # Use existing test sheet
    spreadsheet_id = "1sBJvL_UIDULvZeycsm-PPk0V3_LEXM9fIrWh5osQVCc"
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    
    print(f"\n📋 Usando sheet existente:")
    print(f"   {spreadsheet_url}")
    print(f"   ID: {spreadsheet_id}")
    
    # Read URLs from the sheet to show what will be processed
    print("\n📖 Leyendo URLs del sheet...")
    import os
    from apps.ingestion.google_sheets import GoogleSheetsService
    
    # Set credentials path
    credentials_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'backend', 
        'credentials', 
        'google-sheets-credentials.json'
    )
    
    sheets_service = GoogleSheetsService(credentials_path=credentials_path)
    
    try:
        pending_rows = sheets_service.read_pending_rows(spreadsheet_id)
        
        if not pending_rows:
            print("⚠️  No hay URLs pendientes en el sheet")
            print("\n💡 Agregando URLs de prueba...")
            
            # Add test URLs from found_property_urls.txt
            test_urls = [
                "https://www.coldwellbankercostarica.com/property/land-for-sale-in-curridabat/2785",
                "https://costarica.org/tours/",
                "https://costarica.org/tours/arenal/",
                "https://www.encuentra24.com/costa-rica-es/bienes-raices-proyectos-nuevos/venta-de-apartamento-en-jaco/31553057",
            ]
            
            # Prepare rows: URL, Tipo (empty), Status (empty = pending)
            rows_to_add = [[url, "", ""] for url in test_urls]
            
            # Get the last row to append after it
            result = sheets_service.sheets_api.values().get(
                spreadsheetId=spreadsheet_id,
                range='Template!A:A'
            ).execute()
            
            existing_rows = result.get('values', [])
            next_row = len(existing_rows) + 1
            
            # Append URLs
            sheets_service.append_rows(
                spreadsheet_id,
                f"Template!A{next_row}",
                rows_to_add
            )
            
            print(f"✅ Agregadas {len(test_urls)} URLs nuevas al sheet")
            for i, url in enumerate(test_urls, 1):
                print(f"   {i}. {url}")
            
            # Re-read pending rows
            pending_rows = sheets_service.read_pending_rows(spreadsheet_id)
        
        print(f"✅ Encontradas {len(pending_rows)} URLs pendientes:")
        for i, row in enumerate(pending_rows, 1):
            print(f"   {i}. {row['url']}")
    except Exception as e:
        print(f"❌ Error leyendo sheet: {e}")
        print("   Asegúrate de que el sheet tenga URLs en la columna A")
        return
    
    # Now process the sheet
    print("\n" + "=" * 80)
    print("🔄 PROCESANDO SHEET CON AUTO-TABS")
    print("=" * 80)
    
    payload = {
        "spreadsheet_id": spreadsheet_id,
        "notify_email": "test@example.com",
        "async": False,  # Synchronous for testing
        "create_results_sheet": False  # Write tabs to same sheet
    }
    
    print(f"\n📤 Enviando request a: {api_url}")
    print(f"   Spreadsheet ID: {spreadsheet_id}")
    
    response = requests.post(api_url, json=payload)
    
    if not response.ok:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    
    print("\n" + "=" * 80)
    print("📊 RESULTADOS")
    print("=" * 80)
    
    print(f"\n✅ Status: {result['status']}")
    print(f"   Total URLs: {result['total']}")
    print(f"   Procesadas: {result['processed']}")
    print(f"   Fallidas: {result['failed']}")
    
    if 'tabs' in result and result['tabs']:
        print(f"\n📑 Pestañas creadas: {len(result['tabs'])}")
        for tab in result['tabs']:
            print(f"   • {tab['name']}: {tab['count']} items, {tab['columns']} columnas")
            print(f"     Content Type: {tab['content_type']}, Page Type: {tab['page_type']}")
    else:
        print("\n⚠️  No se crearon pestañas")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
    print(f"\n🔗 Revisa el Google Sheet:")
    print(f"   {spreadsheet_url}")
    print(f"\n   Deberías ver tabs como:")
    print(f"   • real_estate_specific (2 items)")
    print(f"   • tour_general (2 items)")
    print("=" * 80)


if __name__ == "__main__":
    test_google_sheets_auto_tabs()
