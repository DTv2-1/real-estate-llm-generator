"""
Refactorización de Views - Estructura Organizada

ANTES:
- 1 archivo grande: views.py (2106 líneas)
- Todas las vistas mezcladas

DESPUÉS:
- views/ (paquete organizado)
  - __init__.py (exporta todas las vistas)
  - base.py (utilidades compartidas)
  - utility_views.py (SupportedWebsitesView, ContentTypesView, Stats, etc.)
  - basic_ingestion.py (IngestURLView, IngestTextView, SavePropertyView)
  - google_sheets_auto_tabs.py (ProcessGoogleSheetView - solo auto-tabs)
  - batch_processing.py (IngestBatchView, BatchExportToSheetsView, BatchExportToDatabaseView)

ENDPOINTS:
1. BASIC INGESTION (http://localhost:5173/url-ingestion):
   - POST /ingest/url/ → IngestURLView
   - POST /ingest/text/ → IngestTextView
   - POST /ingest/save/ → SavePropertyView

2. GOOGLE SHEETS AUTO-TABS (http://localhost:5173/google-sheets):
   - POST /ingest/google-sheet/ → ProcessGoogleSheetView
   - Lee URLs del sheet
   - Clasifica por content_type + page_type
   - Crea tabs automáticos (real_estate_specific, tour_general, etc.)
   - Exporta a tabs separados EN EL MISMO SHEET

3. BATCH PROCESSING (http://localhost:5173/batch-processing):
   - POST /ingest/batch/ → IngestBatchView
   - POST /ingest/batch-export/sheets/ → BatchExportToSheetsView
   - POST /ingest/batch-export/database/ → BatchExportToDatabaseView
   - Procesa múltiples URLs
   - Exporta a Google Sheets externos
   - Guarda en database

4. UTILITIES:
   - GET /ingest/supported-websites/
   - GET /ingest/content-types/
   - GET /ingest/stats/
   - POST /ingest/generate-embeddings/
   - POST /ingest/create-sheet-template/
   - POST /ingest/cancel-batch/

PRÓXIMOS PASOS:
1. ✅ Crear estructura de carpetas
2. ✅ Crear __init__.py con exports
3. ✅ Crear base.py
4. ✅ Crear utility_views.py
5. ⏳ Crear basic_ingestion.py
6. ⏳ Crear google_sheets_auto_tabs.py
7. ⏳ Crear batch_processing.py
8. ⏳ Actualizar imports en urls.py
9. ⏳ Probar que todo funcione
"""
