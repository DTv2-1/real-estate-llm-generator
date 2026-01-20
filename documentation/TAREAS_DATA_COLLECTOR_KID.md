# TAREAS DATA COLLECTOR - PREPARACIÓN PARA KID

**Fecha:** 19 de enero de 2026  
**Contexto:** Preparar el Data Collector para que el kid pueda alimentar datos cuando llegue su computadora

---

## TAREAS INMEDIATAS (Esta semana - antes de que llegue la computadora del kid)

### 1. Completar funcionalidad de scraping para los 4 tipos de contenido

**Tours:** ✅ COMPLETADO
- Extraer: nombre del tour, descripción, precio, horarios/duración, ubicación, contacto
- Manejar diferentes formatos de páginas de tours
- Prompt específico y general implementados

**Transporte:** ✅ COMPLETADO
- Extraer: tipo de transporte, rutas, horarios, precios, contacto
- Buses, taxis, shuttles, transfers
- Prompt específico y general implementados
- Detección de page_type agregada

**Restaurantes:** ⏳ PENDIENTE
- Extraer: nombre, tipo de comida, horarios, rango de precios, ubicación, menú si está disponible

**Tips/Consejos:** ⏳ PENDIENTE
- Extraer: contenido del tip, categoría, fuente
- Información general útil para turistas

### 2. Crear/mejorar UI simple para el data collector (kid)

**Pantalla principal debe tener:**
- Campo para pegar URL
- Botón de "Scrapear" o "Extraer datos"
- Indicador de progreso mientras scrapeando
- Vista previa de datos extraídos

**Características esenciales:**
- Muy simple, sin opciones técnicas complicadas
- Feedback visual claro (éxito/error)
- Poder ver los datos antes de guardarlos

### 3. Sistema de validación de calidad de datos

**Checklist automático que verifique:**
- ¿Tiene precio/costo? ✓/✗
- ¿Tiene horarios/schedule? ✓/✗
- ¿Tiene descripción completa? ✓/✗
- ¿Tiene información de contacto? ✓/✗

**Mostrar al kid:**
- Score de calidad (ej: 3/4 campos completos)
- Qué campos faltan
- Advertencia si la calidad es baja

### 4. Guardar datos raw y links

**Asegurar que se guarde:**
- URL original de donde vino el dato
- HTML/contenido raw completo
- Fecha de extracción
- Datos normalizados/estructurados

**Por qué:** Kelly mencionó que es importante preservar el link original y datos raw para transparencia

### 5. Preparar documentación simple

**Crear guía paso a paso para el kid:**
- Cómo encontrar páginas web de tours/restaurantes/etc
- Cómo copiar y pegar el link
- Cómo revisar que los datos sean buenos
- Qué hacer si algo falla
- Ejemplos de buenos vs malos resultados

---

## TAREAS PARA PRÓXIMA SEMANA (Cuando llegue la computadora)

### 6. Sesión de entrenamiento con el kid

**Agenda de la sesión:**
- Mostrar cómo funciona la herramienta (30 min)
- Hacer ejemplos juntos con páginas reales (30 min)
- Dejar que él practique mientras observas (30 min)
- Responder preguntas y resolver dudas (30 min)

**Páginas de ejemplo para practicar:**
- Una página simple de tour
- Una página compleja/difícil
- Un restaurante
- Información de transporte

### 7. Definir proceso de trabajo con el kid

**Establecer:**
- Cuántas páginas debe scrapear por día/semana
- Cómo reportar problemas
- Cómo dar feedback sobre calidad
- Frecuencia de revisión contigo

---

## TAREAS POSTERIORES (Después del entrenamiento)

### 8. Soporte y mejoras iterativas

**Mientras el kid trabaja:**
- Estar disponible para preguntas
- Revisar logs de errores
- Identificar páginas que fallan mucho
- Mejorar el scraper basándome en casos reales

### 9. Mejoras al sistema basadas en uso real

**Observar qué problemas encuentra el kid:**
- ¿Qué tipos de páginas no funcionan bien?
- ¿Qué información no se extrae correctamente?
- ¿Qué es confuso en la UI?

### 10. Alimentar el RAG/Chatbot

**Una vez que hay suficientes datos:**
- Conectar los datos scraped al sistema RAG
- Probar que el chatbot pueda responder preguntas
- Iterar basándome en calidad de respuestas

---

## PRIORIZACIÓN

### CRÍTICO (hacer antes de la sesión con el kid):
1. UI funcional y simple
2. Validación de calidad visible
3. Scraping funcionando para los 4 tipos
4. Documentación básica

### IMPORTANTE (pero puede mejorar después):
1. Manejo de errores robusto
2. Bulk scraping (múltiples URLs a la vez)
3. Dashboard de estadísticas

### NICE TO HAVE (futuro):
1. Scraping automático programado
2. Detección de cambios en páginas
3. Notificaciones cuando hay datos nuevos

---

## ESTRATEGIA GENERAL

Kelly dejó claro que después de que el kid esté trabajando alimentando datos, **puedo enfocarme en el proyecto nuevo del LLM personal de Kelly**. Entonces la estrategia es:

1. **Esta semana:** Hacer el Data Collector suficientemente bueno y simple
2. **Próxima semana:** Entrenar al kid
3. **Después:** El kid trabaja independientemente, yo paso al proyecto del LLM
4. **Ocasionalmente:** Doy soporte al kid si tiene problemas

---

## NOTAS ADICIONALES

- El sistema debe ser lo suficientemente robusto para funcionar sin supervisión constante
- La UI debe ser intuitiva para alguien sin experiencia técnica
- El feedback de calidad es crucial para que el kid sepa si está haciendo bien su trabajo
- Preservar datos raw es importante para auditoría y mejoras futuras
