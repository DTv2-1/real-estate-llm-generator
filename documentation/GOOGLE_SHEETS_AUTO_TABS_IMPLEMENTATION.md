# Google Sheets Auto-Tab Implementation
## Resumen de Cambios - 17 de Enero, 2026

### 🎯 Objetivo
Actualizar la página de Google Sheets (`/google-sheets`) para que use la misma lógica de clasificación y creación automática de tabs que el procesamiento por lotes, con nombres de tabs en formato `tipo_page` (ej: `tour_general`, `real_estate_specific`).

---

## 📋 Cambios Realizados

### 1. Backend: ProcessGoogleSheetView (views.py)

**Ubicación:** `backend/apps/ingestion/views.py` - Clase `ProcessGoogleSheetView`

#### Métodos Agregados:
- `_get_column_schema(content_type, page_type)`: Reutiliza el esquema de columnas de BatchExportToSheetsView
- `_extract_field_value(obj, key_path)`: Reutiliza la lógica de extracción de BatchExportToSheetsView

#### Lógica de Procesamiento Actualizada:
```python
# Proceso anterior: Simple procesamiento sin clasificación
# Proceso nuevo: Clasificación automática + creación de tabs

1. Lee URLs del Google Sheet
2. Procesa cada URL y extrae content_type y page_type de la Property
3. Clasifica resultados en grupos: {content_type}_{page_type}
4. Para cada grupo:
   - Crea/obtiene la pestaña con nombre "tour_general", "real_estate_specific", etc.
   - Limpia la pestaña
   - Aplica el schema de columnas correcto (19-22 columnas según tipo)
   - Escribe datos con formato inteligente (FAQs, seasonal activities, etc.)
5. Retorna info de las pestañas creadas
```

#### Características:
- ✅ Clasificación automática por content_type y page_type
- ✅ Nombres de tabs: `{content_type}_{page_type}` (ej: `tour_general`)
- ✅ Creación automática de pestañas
- ✅ Limpieza de sheets antes de escribir (no duplicados)
- ✅ Schemas de columnas correctos (19-22 columnas)
- ✅ Formateo inteligente de arrays (FAQs, actividades)
- ✅ Actualización de status en sheet original
- ✅ Soporte para results_sheet separado (opcional)

#### Response Format:
```json
{
  "status": "completed",
  "total": 4,
  "processed": 4,
  "failed": 0,
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...",
  "tabs": [
    {
      "name": "real_estate_specific",
      "count": 2,
      "columns": 19,
      "content_type": "real_estate",
      "page_type": "specific"
    },
    {
      "name": "tour_general",
      "count": 2,
      "columns": 22,
      "content_type": "tour",
      "page_type": "general"
    }
  ]
}
```

---

### 2. Frontend: GoogleSheetsIntegration.tsx

**Ubicación:** `frontend/src/components/GoogleSheetsIntegration.tsx`

#### Cambios:
1. **API_BASE actualizado**: `localhost:8080` → `localhost:8000`
2. **Mensaje de éxito mejorado**: Muestra pestañas creadas con formato:
   ```
   ✅ Completado! Procesadas: 4, Fallidas: 0, Total: 4.
   Se crearon 2 pestañas: real_estate_specific (2 items), tour_general (2 items)
   ```

#### Código Actualizado:
```typescript
if (data.status === 'completed') {
  const tabs = data.tabs || []
  
  let successMessage = `✅ Completado! Procesadas: ${processed}, Fallidas: ${failed}, Total: ${total}.`
  
  if (tabs.length > 0) {
    successMessage += ' Se crearon ' + tabs.length + ' pestañas: '
    successMessage += tabs.map((t: any) => `${t.name} (${t.count} items)`).join(', ')
  }
  
  if (data.results_spreadsheet) {
    successMessage += ' | Resultados en: ' + data.results_spreadsheet.spreadsheet_url
  }
}
```

---

## 🧪 Script de Prueba

**Ubicación:** `testing/test_google_sheets_auto_tabs.py`

### Qué hace:
1. Crea un template sheet nuevo
2. Agrega 4 URLs de prueba:
   - 2 propiedades de real estate (specific)
   - 2 páginas de tours (general)
3. Procesa el sheet con la lógica nueva
4. Muestra las pestañas creadas

### Ejecutar:
```bash
cd /Users/1di/kp-real-estate-llm-prototype
python testing/test_google_sheets_auto_tabs.py
```

### Output Esperado:
```
🧪 TEST: GOOGLE SHEETS AUTO-TAB CREATION
================================================================================
📋 Creando template sheet...
✅ Template creado: https://docs.google.com/spreadsheets/d/...
   ID: ...

📝 Agregando URLs al sheet...
✅ Agregadas 4 URLs al sheet
   1. https://www.coldwellbankercostarica.com/property/land-for-sale-in-curridabat/2785
   2. https://www.coldwellbankercostarica.com/property/land-for-sale-in-uvita/3899
   3. https://costarica.org/tours/
   4. https://costarica.org/tours/arenal/

================================================================================
🔄 PROCESANDO SHEET CON AUTO-TABS
================================================================================

================================================================================
📊 RESULTADOS
================================================================================

✅ Status: completed
   Total URLs: 4
   Procesadas: 4
   Fallidas: 0

📑 Pestañas creadas: 2
   • real_estate_specific: 2 items, 19 columnas
     Content Type: real_estate, Page Type: specific
   • tour_general: 2 items, 22 columnas
     Content Type: tour, Page Type: general

================================================================================
✅ TEST COMPLETADO
================================================================================

🔗 Revisa el Google Sheet:
   https://docs.google.com/spreadsheets/d/...

   Deberías ver tabs como:
   • real_estate_specific (2 items)
   • tour_general (2 items)
================================================================================
```

---

## 🔄 Flujo Completo

### Usuario en `/google-sheets`:
1. Crea o usa template existente
2. Pega URLs en columna A
3. Click "Procesar Sheet"
4. Sistema:
   - Procesa cada URL
   - Detecta tipo (tour, real_estate, restaurant)
   - Detecta si es específico o general
   - Agrupa por clasificación
   - Crea tabs automáticamente: `tour_general`, `real_estate_specific`, etc.
5. Usuario ve mensaje: "Se crearon 2 pestañas: tour_general (2 items), real_estate_specific (2 items)"
6. Usuario abre el sheet y ve las pestañas organizadas

---

## ✅ Beneficios

1. **Consistencia**: Misma lógica que batch processing
2. **Organización**: Datos clasificados automáticamente
3. **Naming claro**: Formato `tipo_page` es descriptivo
4. **Sin duplicados**: Sheets se limpian antes de escribir
5. **Schemas correctos**: Cada tipo tiene sus columnas específicas
6. **Formateo inteligente**: FAQs, actividades, etc. legibles

---

## 🚀 Próximos Pasos

1. Ejecutar test script para validar funcionamiento
2. Probar frontend en `http://localhost:5173/google-sheets`
3. Verificar que las pestañas se crean correctamente
4. Confirmar que los datos se formatean bien
5. Validar mensajes de éxito en UI

---

## 📝 Notas Técnicas

- Backend usa `Property.content_type` y `Property.page_type` para clasificación
- Formato de tab: `{content_type}_{page_type}` (guion bajo, no espacio)
- Reutiliza métodos de `BatchExportToSheetsView` para mantener consistencia
- Soporta escritura en mismo sheet o results_sheet separado
- Updates status en sheet original ("Procesado" o "Error")

---

**Fecha:** 17 de Enero, 2026  
**Estado:** ✅ Implementación completa  
**Testing:** 🧪 Script de prueba listo
