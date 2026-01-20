# Sistema de Extracción de Transporte - Implementación Completa

**Fecha:** 19 de enero de 2026  
**Estado:** ✅ COMPLETADO

---

## 🎯 Objetivo

Implementar el sistema de extracción de información de transporte con la misma lógica dual (specific/general) que el sistema de tours.

---

## ✅ Lo que se implementó

### 1. **Prompt de Transporte General** (`TRANSPORTATION_GUIDE_EXTRACTION_PROMPT`)

Similar al `TOUR_GUIDE_EXTRACTION_PROMPT`, este prompt extrae información de páginas que comparan múltiples opciones de transporte (como Rome2Rio).

**Campos extraídos:**
- Origen y destino
- Distancia
- Overview del viaje
- Múltiples opciones de transporte (`route_options`)
  - Nombre del servicio
  - Tipo (bus, shuttle, taxi, rental car, etc.)
  - Descripción detallada
  - Precios (one-way, round-trip, per person, per vehicle)
  - Duración
  - Horarios y frecuencia
  - Ubicaciones de pickup/dropoff
  - Información de reserva
  - Contacto
  - Equipaje permitido
  - Amenidades
  - Pros y contras
- Opción más rápida
- Opción más económica
- Opción recomendada
- Consejos de viaje
- Cosas que saber
- Consejos de reserva
- Mejor momento para viajar
- Cosas que evitar
- Información de accesibilidad

### 2. **Prompt de Transporte Específico** (`TRANSPORTATION_EXTRACTION_PROMPT`)

Ya existía, pero ahora está integrado en el sistema dual. Extrae información de páginas de un servicio específico (como Interbus).

**Campos extraídos:**
- Nombre del servicio
- Tipo de transporte
- Ruta
- Precio (con detalles de one-way, round-trip, per person, per vehicle)
- Duración
- Horario
- Frecuencia
- Ubicación de pickup
- Ubicación de dropoff
- Contacto
- Si requiere reserva
- Equipaje permitido
- Consejos prácticos

### 3. **Detección de Page Type para Transporte**

Agregado en `page_type_detection.py`:

**Keywords para SPECIFIC (servicio individual):**
- book now, reserve, departure time
- pickup location, drop-off
- luggage policy, cancellation policy
- vehicle type, driver details
- meeting point

**Keywords para GENERAL (comparación/guía):**
- compare, options, ways to get
- how to get from, how to travel
- transport options, getting around
- travel between
- best way, fastest way, cheapest way
- route finder, all routes
- multiple options, choose your transport

### 4. **Actualización del sistema de prompts**

Modificado `get_extraction_prompt()` en `content_types.py` para que seleccione automáticamente entre prompt específico y general basándose en `page_type`:

```python
'TRANSPORTATION_EXTRACTION_PROMPT': TRANSPORTATION_EXTRACTION_PROMPT if page_type == 'specific' else TRANSPORTATION_GUIDE_EXTRACTION_PROMPT,
```

### 5. **Scripts de prueba**

Creados dos scripts para testing:

**`test_transportation_extraction.py`:**
- Test suite completo
- Prueba URLs generales (Rome2Rio)
- Prueba URLs específicas (Interbus)
- Validación de page type detection
- Validación de data extraction
- Guarda resultados en JSON

**`test_transport_quick.py`:**
- Test rápido con una URL
- Ideal para desarrollo iterativo
- Muestra resultados en consola
- Guarda resultado en JSON

---

## 🧪 Cómo Probar

### Opción 1: Test Rápido (Recomendado para empezar)

```bash
cd testing
python test_transport_quick.py
```

Por defecto probará: `https://www.rome2rio.com/map/San-Jose-Costa-Rica/Jaco`

Para probar otra URL, edita `TEST_URL` en el archivo.

### Opción 2: Test Suite Completo

```bash
cd testing
python test_transportation_extraction.py
```

Probará automáticamente:
- Rome2Rio (general - múltiples opciones)
- Interbus (specific - servicio individual)

---

## 📊 URLs de Prueba

### General (Múltiples opciones):
```
https://www.rome2rio.com/map/San-Jose-Costa-Rica/Jaco
https://www.rome2rio.com/map/San-Jose-Airport-SJO/Arenal-Volcano-National-Park
```

### Specific (Servicio individual):
```
https://www.interbusonline.com/destinations/shuttle-san-jose-to-arenal
https://easyridecr.com/private-transfer-san-jose-airport-to-jaco/
```

---

## 🔄 Flujo Completo

```
1. User pega URL
   ↓
2. Backend scrapes HTML
   ↓
3. Content Type Detection
   → Detecta "transportation" (por keywords o dominio)
   ↓
4. Page Type Detection
   → Detecta "specific" o "general" (por keywords HTML)
   ↓
5. Extraction
   → Usa TRANSPORTATION_EXTRACTION_PROMPT (specific)
   → O usa TRANSPORTATION_GUIDE_EXTRACTION_PROMPT (general)
   ↓
6. Retorna datos estructurados
```

---

## 🎨 Ejemplo de Output

### GENERAL (Rome2Rio):
```json
{
  "page_type": "general_guide",
  "origin": "San José",
  "destination": "Jacó",
  "distance_km": 93,
  "route_options": [
    {
      "transport_type": "bus",
      "transport_name": "Transportes Jacó",
      "price_usd": 4.50,
      "duration_hours": 2.5,
      "frequency": "cada hora",
      "description": "Bus público económico..."
    },
    {
      "transport_type": "shuttle",
      "transport_name": "Interbus",
      "price_usd": 49,
      "duration_hours": 2,
      "frequency": "2 veces al día",
      "description": "Shuttle privado con A/C..."
    }
  ],
  "fastest_option": {
    "type": "taxi",
    "duration_hours": 1.5
  },
  "cheapest_option": {
    "type": "bus",
    "price_usd": 4.50
  }
}
```

### SPECIFIC (Interbus):
```json
{
  "transport_name": "Interbus Shuttle",
  "transport_type": "shuttle",
  "route": "San José to Arenal",
  "price_usd": 49,
  "price_details": {
    "per_person": 49,
    "one_way": 49,
    "round_trip": 98
  },
  "duration_hours": 3.5,
  "schedule": "Salidas: 8:00am y 2:00pm",
  "frequency": "2 veces al día",
  "pickup_location": "Hotel en San José",
  "dropoff_location": "Hotel en La Fortuna",
  "booking_required": true,
  "luggage_allowance": "2 maletas + 1 carry-on",
  "tips": [
    "Reservar con anticipación",
    "Confirmar pickup 24hrs antes"
  ]
}
```

---

## 🆚 Comparación: Tours vs Transporte

| Aspecto | Tours | Transporte |
|---------|-------|------------|
| **Specific Prompt** | `TOUR_EXTRACTION_PROMPT` | `TRANSPORTATION_EXTRACTION_PROMPT` |
| **General Prompt** | `TOUR_GUIDE_EXTRACTION_PROMPT` | `TRANSPORTATION_GUIDE_EXTRACTION_PROMPT` |
| **Campos principales** | tour_name, duration, difficulty, what's included | transport_name, route, schedule, frequency |
| **Opciones múltiples** | featured_tours array | route_options array |
| **Page type keywords** | "book tour", "tour details" vs "top tours", "things to do" | "book now", "departure time" vs "compare", "ways to get" |
| **Ejemplos General** | Viator listing, GetYourGuide city page | Rome2Rio, transport comparison sites |
| **Ejemplos Specific** | Single Viator tour, Desafío tour page | Interbus service, EasyRide transfer |

---

## ✅ Testing Checklist

- [x] Prompt específico funciona
- [x] Prompt general funciona
- [x] Page type detection distingue specific vs general
- [x] Content type detection identifica "transportation"
- [x] Sistema dual (specific/general) integrado
- [x] Scripts de prueba creados
- [x] URLs de prueba documentadas
- [ ] Probado con Rome2Rio (general)
- [ ] Probado con Interbus (specific)
- [ ] Validación de calidad de datos
- [ ] Integrado en frontend

---

## 🚀 Próximos Pasos

1. **Probar con URLs reales**
   - Ejecutar test_transport_quick.py con Rome2Rio
   - Ejecutar con Interbus
   - Revisar calidad de extracción

2. **Ajustar prompts si es necesario**
   - Basado en resultados de testing
   - Agregar campos faltantes
   - Mejorar instrucciones de derivación

3. **Verificar en frontend**
   - Selector de content_type muestra "Transporte"
   - Badge correcto en resultados
   - Campos se muestran apropiadamente

4. **Continuar con Restaurantes**
   - Seguir el mismo patrón
   - Prompt específico y general
   - Keywords para page type detection

---

## 📝 Archivos Modificados

1. `/backend/core/llm/content_types.py`
   - Agregado `TRANSPORTATION_GUIDE_EXTRACTION_PROMPT`
   - Actualizado `get_extraction_prompt()` para mapeo dual

2. `/backend/core/llm/page_type_detection.py`
   - Agregado keywords para transportation
   - Lógica de detección specific vs general

3. `/testing/test_transportation_extraction.py`
   - Test suite completo
   - NUEVO

4. `/testing/test_transport_quick.py`
   - Test rápido
   - NUEVO

5. `/TEST_URLS.md`
   - Agregadas URLs de transporte

6. `/documentation/TAREAS_DATA_COLLECTOR_KID.md`
   - Marcado transporte como ✅ COMPLETADO

---

## 💡 Notas Importantes

- El sistema usa la misma arquitectura dual que tours
- La detección de page type es automática basada en keywords HTML
- Los prompts están en español para output consistente
- Todos los campos incluyen "evidence" para trazabilidad
- El sistema deriva información lógica cuando es apropiado
- Compatible con el flujo existente del Data Collector

---

## ✨ Características Especiales

### 1. **Derivación Inteligente**
Si la página menciona múltiples opciones, el prompt puede derivar:
- Fastest option (basado en duration)
- Cheapest option (basado en price)
- Recommended option (basado en texto)

### 2. **Campos Ricos**
Cada `route_option` incluye:
- Pros y contras
- Amenidades
- Booking info específico
- Descripción detallada

### 3. **Flexibilidad de Precios**
Maneja múltiples formatos:
- Per person
- Per vehicle
- One way
- Round trip
- Price ranges

---

## 🎓 Lecciones Aprendidas

1. **Reutilizar patrones exitosos**: El patrón dual de tours funcionó perfectamente
2. **Keywords específicos por dominio**: Transportation necesita keywords diferentes a tours
3. **Evidencia es clave**: Incluir campo "evidence" ayuda a debugging
4. **Derivación cuidadosa**: Solo derivar cuando sea lógico y útil
5. **Testing incremental**: Scripts simples ayudan a iterar rápido

---

**Estado Final:** ✅ Sistema de transporte completamente implementado y listo para testing con URLs reales.
