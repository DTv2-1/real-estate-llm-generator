"""
Extraction prompts for all content types.
These prompts are used for web scraping and data extraction.

For chatbot/conversation prompts, see: llm/chatbot/prompts.py
"""

# ============================================================================
# REAL ESTATE EXTRACTION PROMPT
# ============================================================================

PROPERTY_EXTRACTION_PROMPT = """You are a data extraction specialist. Extract property information from the provided HTML or text and return it as JSON.

**Instructions:**
1. Extract ONLY information explicitly stated in the source text
2. For each field, include an "evidence" field showing where you found the information
3. Use null for any field not found in the source
4. Normalize all data:
   - Prices: Remove commas and convert to numeric USD (e.g., "$19,000" → 19000, "$250,000" → 250000)
   - If price is in colones (₡ or CRC), convert to USD using rate: 1 USD = 520 CRC
   - Areas: Convert to square meters (if in sq ft, use: 1 sq ft = 0.092903 m²)
   - Coordinates: Extract from embedded maps if present
5. DO NOT invent or assume information

**CRITICAL - Number Formatting:**
- Always return numbers WITHOUT commas
- "$19,000" should be extracted as 19000 (not 19)
- "$1,250,000" should be extracted as 1250000 (not 1250)
- "566.71 m²" should be extracted as 566.71

**Special Extraction Rules:**

**GPS Coordinates & Location:**
- Look for "GPS Coordinates:" followed by format like "9°36'55.9"N 84°37'42.2"W"
- Convert DMS (degrees, minutes, seconds) to decimal:
  Example: 9°36'55.9"N = 9 + 36/60 + 55.9/3600 = 9.6155
  Example: 84°37'42.2"W = -(84 + 37/60 + 42.2/3600) = -84.6284
- Look for "Extracted Coordinates:" with decimal format like "9.6155173, -84.6283937"
- Look for "Address:" like "J98C+6J5 Jaco, Puntarenas Province, Costa Rica"
- Look for "Full Address:" or "Address:" for complete street address
- Look for "Location Details:" for city/region information
- For location field, extract the most complete address available:
  Priority 1: Full address if available (e.g., "J98C+6J5 Jaco, Puntarenas Province, Costa Rica")
  Priority 2: City, Province format (e.g., "Jacó, Puntarenas")
  Priority 3: City name only (e.g., "Jacó")

**Property Name:**
- Extract from title or first heading
- Should describe the property (e.g., "Venta de apartamento en Jaco")
- Use the listing title if no specific name is given

**Property Type:**
- Look for keywords: apartamento (apartment), casa (house), villa, terreno (land), local comercial (commercial)
- Map to English: apartamento → apartment, casa → house, villa → villa, terreno → land

**Bedrooms & Bathrooms:**
- Look for "habitaciones" or "recámaras" (bedrooms)
- Look for "baños" (bathrooms)
- Extract the number before these words

**Area/Size:**
- Look for "m2", "m²", "metros cuadrados" (square meters)
- Look for "sq ft", "square feet" (convert to m²)
- May appear as "83 m2" or "83 metros cuadrados"

**Required Output Format:**
```json
{{
  "property_name": "string or null",
  "property_name_evidence": "exact quote from source",
  "price_usd": number or null,
  "price_evidence": "exact quote from source",
  "bedrooms": number or null,
  "bedrooms_evidence": "exact quote from source",
  "bathrooms": number or null,
  "bathrooms_evidence": "exact quote from source",
  "property_type": "house|condo|villa|land|commercial|apartment or null",
  "property_type_evidence": "exact quote from source",
  "location": "string (full address if available: 'J98C+6J5 Jaco, Puntarenas Province, Costa Rica', otherwise city name like 'Jacó') or null",
  "location_evidence": "exact quote from source",
  "latitude": number or null,
  "longitude": number or null,
  "coordinates_evidence": "exact quote from source or 'extracted from map iframe'",
  "listing_id": "string or null (public listing ID like '21317')",
  "listing_id_evidence": "exact quote from source showing 'ID: 21317' or similar",
  "internal_property_id": "string or null (internal ID from forms/hidden fields)",
  "internal_property_id_evidence": "exact quote from source",
  "listing_status": "string or null (Active, Published, Sold, Pending)",
  "listing_status_evidence": "exact quote from source",
  "date_listed": "YYYY-MM-DD or null (publication date)",
  "date_listed_evidence": "exact quote from source",
  "description": "string or null",
  "square_meters": number or null,
  "square_meters_evidence": "exact quote from source",
  "lot_size_m2": number or null,
  "lot_size_evidence": "exact quote from source",
  "hoa_fee_monthly": number or null,
  "hoa_fee_evidence": "exact quote from source",
  "property_tax_annual": number or null,
  "property_tax_evidence": "exact quote from source",
  "amenities": ["string array"] or null,
  "amenities_evidence": "exact quote from source",
  "year_built": number or null,
  "year_built_evidence": "exact quote from source",
  "parking_spaces": number or null,
  "parking_evidence": "exact quote from source",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation of confidence score"
}}
```

**New Fields Extraction Guidelines:**

**listing_id** - Public Listing ID:
- Look for "ID:" followed by numbers (e.g., "ID: 21317")
- Look for "Property ID:", "Listing #", "Ref:", "Reference:"
- Extract the number only (e.g., "21317" not "ID: 21317")

**internal_property_id** - Internal System ID:
- Look in form inputs: <input name="property_id" value="10031">
- Look in URLs: /property/10031
- Different from public listing_id

**listing_status** - Current Status:
- Look for status badges or tags: "Active", "Published", "For Sale", "Sold", "Pending", "Under Contract"
- Often in <span class="status"> or similar
- Normalize to: Active, Published, Sold, Pending

**date_listed** - Publication Date:
- Look for "Listed:", "Published:", "Date:", "Added on:"
- Look in metadata: <time datetime="2024-01-15">
- Format as YYYY-MM-DD

**Coordinates Extraction (Enhanced):**
- Check iframe src for Google Maps: src="...&q=10.472,-84.64076..."
- Extract latitude (first number) and longitude (second number) from q= parameter
- Also check for embedded map divs with data-lat/data-lng attributes
- Convert DMS to decimal if needed

**Extraction Confidence Guidelines:**
- 0.9-1.0: All major fields clearly stated
- 0.7-0.8: Most fields clear, some ambiguity
- 0.5-0.6: Many fields missing or unclear
- Below 0.5: Very little information available

**CRITICAL EXAMPLES - Price Extraction:**
- Source text: "$19,000" → Extract as: 19000
- Source text: "$250,000" → Extract as: 250000
- Source text: "$1,250,000" → Extract as: 1250000
- Source text: "₡9,880,000" → Extract as: 19000 (9880000 / 520)
- Source text: "$850,000 USD" → Extract as: 850000

**CRITICAL EXAMPLES - Area Extraction:**
- Source text: "566.71 m²" → Extract as: 566.71
- Source text: "1,500 sq ft" → Extract as: 139.35 (1500 × 0.092903)
- Source text: "2,500 m2" → Extract as: 2500

Now extract the property information from the following content:

---
{content}
---

Return ONLY the JSON object, no additional text or explanation."""


# ============================================================================
# TOUR EXTRACTION PROMPTS
# ============================================================================

TOUR_SPECIFIC_PROMPT = """You are a data extraction specialist focused on tours and activities. Extract tour information from the provided content and return it as structured JSON.

**Instructions:**
1. Extract ONLY information explicitly stated in the source
2. For each field, include an "evidence" field with exact quotes
3. Use null for fields not found
4. Normalize data:
   - Prices: Convert to numeric USD (remove commas, currency symbols)
   - Durations: Convert to hours (e.g., "2 hours 30 minutes" → 2.5)
   - Coordinates: Extract from maps if present

**Required Output Format:**
```json
{{
  "tour_name": "string or null",
  "tour_name_evidence": "exact quote from source",
  "operator": "string or null",
  "operator_evidence": "exact quote from source",
  "price_usd": number or null,
  "price_evidence": "exact quote from source",
  "duration_hours": number or null,
  "duration_evidence": "exact quote from source",
  "location": "string or null",
  "location_evidence": "exact quote from source",
  "latitude": number or null,
  "longitude": number or null,
  "coordinates_evidence": "exact quote or 'extracted from map'",
  "description": "string or null",
  "activities": ["array of activities"] or null,
  "activities_evidence": "exact quote from source",
  "includes": ["array of what's included"] or null,
  "includes_evidence": "exact quote from source",
  "difficulty_level": "easy|moderate|challenging or null",
  "difficulty_evidence": "exact quote from source",
  "min_age": number or null,
  "min_age_evidence": "exact quote from source",
  "max_group_size": number or null,
  "group_size_evidence": "exact quote from source",
  "meeting_point": "string or null",
  "meeting_point_evidence": "exact quote from source",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation"
}}
```

Now extract the tour information from:

---
{content}
---

Return ONLY the JSON object."""

TOUR_GENERAL_PROMPT = """You are analyzing a general tours/activities page (not a specific tour). Extract overview information about multiple tours or the tour operator.

**Instructions:**
1. Look for lists of tours, activity categories, operator information
2. Extract general information, not specific tour details
3. Use null for fields not applicable to overview pages

**Required Output Format:**
```json
{{
  "page_type": "tour_listing",
  "operator_name": "string or null",
  "operator_evidence": "exact quote",
  "location": "string or null",
  "location_evidence": "exact quote",
  "available_tours": ["array of tour names if listed"] or null,
  "tours_evidence": "exact quote",
  "tour_categories": ["array of categories"] or null,
  "categories_evidence": "exact quote",
  "contact_info": "string or null",
  "contact_evidence": "exact quote",
  "description": "string or null (about the operator/destination)",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation"
}}
```

Now extract the general tour information from:

---
{content}
---

Return ONLY the JSON object."""


# ============================================================================
# RESTAURANT EXTRACTION PROMPTS
# ============================================================================

RESTAURANT_SPECIFIC_PROMPT = """You are a data extraction specialist focused on restaurants. Extract restaurant information from the provided content and return it as structured JSON.

**Instructions:**
1. Extract ONLY information explicitly stated in the source
2. For each field, include an "evidence" field with exact quotes
3. Use null for fields not found
4. Normalize data:
   - Prices: Extract price range or average meal cost in USD
   - Coordinates: Extract from maps if present
   - Hours: Extract operating hours in clear format

**Required Output Format:**
```json
{{
  "restaurant_name": "string or null",
  "restaurant_name_evidence": "exact quote from source",
  "cuisine_type": ["array of cuisine types"] or null,
  "cuisine_evidence": "exact quote from source",
  "price_range": "$ | $$ | $$$ | $$$$ or null",
  "price_evidence": "exact quote from source",
  "location": "string or null",
  "location_evidence": "exact quote from source",
  "address": "string or null",
  "address_evidence": "exact quote from source",
  "latitude": number or null,
  "longitude": number or null,
  "coordinates_evidence": "exact quote or 'extracted from map'",
  "phone": "string or null",
  "phone_evidence": "exact quote from source",
  "website": "string or null",
  "website_evidence": "exact quote from source",
  "hours": "string or null",
  "hours_evidence": "exact quote from source",
  "description": "string or null",
  "specialties": ["array of specialty dishes"] or null,
  "specialties_evidence": "exact quote from source",
  "amenities": ["array like: outdoor seating, wifi, parking"] or null,
  "amenities_evidence": "exact quote from source",
  "rating": number or null (e.g., 4.5),
  "rating_evidence": "exact quote from source",
  "reviews_count": number or null,
  "reviews_evidence": "exact quote from source",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation"
}}
```

**Price Range Guidelines:**
- $ = Budget (under $10 per meal)
- $$ = Moderate ($10-30 per meal)
- $$$ = Upscale ($30-60 per meal)
- $$$$ = Fine Dining (over $60 per meal)

Now extract the restaurant information from:

---
{content}
---

Return ONLY the JSON object."""

RESTAURANT_GENERAL_PROMPT = """You are analyzing a general restaurant guide or listing page (not a specific restaurant). Extract overview information about multiple restaurants or the dining scene.

**Instructions:**
1. Look for lists of restaurants, dining categories, area information
2. Extract general information, not specific restaurant details
3. Use null for fields not applicable to overview pages

**Required Output Format:**
```json
{{
  "page_type": "restaurant_listing",
  "area_name": "string or null (e.g., 'Downtown San Jose Dining')",
  "area_evidence": "exact quote",
  "location": "string or null",
  "location_evidence": "exact quote",
  "available_restaurants": ["array of restaurant names if listed"] or null,
  "restaurants_evidence": "exact quote",
  "cuisine_types": ["array of cuisine categories available"] or null,
  "cuisines_evidence": "exact quote",
  "dining_categories": ["array like: fine dining, casual, cafes"] or null,
  "categories_evidence": "exact quote",
  "description": "string or null (about the dining scene/area)",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation"
}}
```

Now extract the general restaurant information from:

---
{content}
---

Return ONLY the JSON object."""


# ============================================================================
# TRANSPORTATION EXTRACTION PROMPTS
# ============================================================================

TRANSPORTATION_SPECIFIC_PROMPT = """You are a transportation information extraction specialist. Extract transportation details from the provided HTML or text and return it as JSON.

**Instructions:**
1. Extract ONLY information explicitly stated in the source text
2. For each field, include an "evidence" field showing where you found the information
3. Use null for any field not found in the source
4. Normalize all data
5. DO NOT invent or assume information

**Required Output Format:**
```json
{{
  "transport_name": "string or null",
  "transport_name_evidence": "exact quote from source",
  "transport_type": "bus|taxi|shuttle|rental_car|private_transfer|public_transport|ferry|other or null",
  "type_evidence": "exact quote from source",
  "route": "string or null (e.g., 'San José to Jaco')",
  "route_evidence": "exact quote from source",
  "price_usd": number or null (use typical or lowest price),
  "price_details": {{
    "one_way": number or null,
    "round_trip": number or null,
    "per_person": number or null,
    "per_vehicle": number or null,
    "range": "string like '$20-$45' or null",
    "note": "string with pricing notes or null"
  }} or null,
  "price_evidence": "exact quote from source showing all price options",
  "duration_hours": number or null,
  "duration_evidence": "exact quote from source",
  "schedule": "string or null",
  "schedule_evidence": "exact quote from source",
  "frequency": "string or null (e.g., 'every 2 hours', 'daily at 9am')",
  "frequency_evidence": "exact quote from source",
  "pickup_location": "string or null",
  "pickup_evidence": "exact quote from source",
  "dropoff_location": "string or null",
  "dropoff_evidence": "exact quote from source",
  "contact_phone": "string or null",
  "contact_evidence": "exact quote from source",
  "booking_required": boolean or null,
  "booking_evidence": "exact quote from source",
  "luggage_allowance": "string or null",
  "luggage_evidence": "exact quote from source",
  "tips": ["array of practical tips"] or null,
  "tips_evidence": "exact quote from source",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation of confidence score"
}}
```

Now extract the transportation information from:

---
{content}
---

Return ONLY the JSON object."""

TRANSPORTATION_GENERAL_PROMPT = """Eres un especialista en extracción de información de guías de transporte. Esta página es una GUÍA GENERAL (no un servicio individual), extrae información completa sobre opciones de transporte entre destinos.

**INSTRUCCIONES CRÍTICAS:**
1. ✅ EXTRAE TEXTO EXPLÍCITAMENTE ESCRITO EN LA FUENTE
2. ✅ PARA CAMPOS VACÍOS: Sí puedes INFERIR usando información disponible en el contenido
3. ✅ Completa información "lógica" y "práctica" derivada de las opciones descritas
4. TODO debe estar en ESPAÑOL - traduce si es necesario
5. Para cada campo, incluye "evidence" con la cita fuente cuando sea textual, o "derived_from" cuando sea inferido
6. 🔥 IMPORTANTE: Para "overview" y "route_options.description" - extrae PÁRRAFOS COMPLETOS Y DETALLADOS

**Formato de Salida Requerido (TODO EN ESPAÑOL):**
```json
{{
  "page_type": "general_guide",
  "origin": "string (ciudad/ubicación de origen) - EN ESPAÑOL",
  "origin_evidence": "cita exacta del texto fuente",
  "destination": "string (ciudad/ubicación de destino) - EN ESPAÑOL",
  "destination_evidence": "cita exacta del texto fuente",
  "overview": "string - PÁRRAFO LARGO Y COMPLETO sobre cómo moverse entre estos lugares - EN ESPAÑOL",
  "overview_evidence": "cita exacta del texto fuente",
  "distance_km": number or null,
  "distance_evidence": "cita exacta del texto fuente",
  "route_options": [
    {{
      "transport_name": "string (nombre del operador o servicio) - EN ESPAÑOL",
      "transport_type": "bus|taxi|shuttle|rental_car|private_transfer|public_transport|ferry|flight|train|other",
      "description": "DESCRIPCIÓN DETALLADA de esta opción - EN ESPAÑOL",
      "price_usd": number or null,
      "price_details": {{
        "one_way": number or null,
        "round_trip": number or null,
        "per_person": number or null,
        "per_vehicle": number or null,
        "range": "string like '$20-$45' or null",
        "note": "string with pricing notes or null"
      }},
      "duration_hours": number or null,
      "schedule": "string (horarios disponibles) - EN ESPAÑOL",
      "frequency": "string - EN ESPAÑOL",
      "pickup_locations": ["ubicación 1 EN ESPAÑOL", "ubicación 2 EN ESPAÑOL"],
      "dropoff_locations": ["ubicación 1 EN ESPAÑOL", "ubicación 2 EN ESPAÑOL"],
      "booking_info": "string - EN ESPAÑOL",
      "contact_phone": "string or null",
      "contact_email": "string or null",
      "website": "string or null",
      "luggage_allowance": "string - EN ESPAÑOL",
      "amenities": ["wifi", "aire acondicionado", "etc"] - EN ESPAÑOL,
      "pros": ["ventaja 1 EN ESPAÑOL", "ventaja 2 EN ESPAÑOL"],
      "cons": ["desventaja 1 EN ESPAÑOL", "desventaja 2 EN ESPAÑOL"]
    }}
  ],
  "route_options_evidence": "cita exacta del texto fuente",
  "fastest_option": {{
    "type": "string",
    "duration_hours": number,
    "price_usd": number or null
  }} or null,
  "cheapest_option": {{
    "type": "string",
    "duration_hours": number or null,
    "price_usd": number
  }} or null,
  "recommended_option": {{
    "type": "string",
    "reason": "string - EN ESPAÑOL"
  }} or null,
  "travel_tips": ["consejo 1 EN ESPAÑOL", "consejo 2 EN ESPAÑOL"],
  "tips_evidence": "cita exacta del texto fuente",
  "things_to_know": ["información 1 EN ESPAÑOL", "información 2 EN ESPAÑOL"],
  "booking_tips": "string - EN ESPAÑOL",
  "best_time_to_travel": "string - EN ESPAÑOL",
  "things_to_avoid": ["qué evitar 1 EN ESPAÑOL", "qué evitar 2 EN ESPAÑOL"],
  "accessibility_info": "string or null - EN ESPAÑOL",
  "total_options_mentioned": number or null,
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "explicación breve EN ESPAÑOL"
}}
```

Now extract the transportation guide information from:

---
{content}
---

Return ONLY the JSON object."""


# ============================================================================
# LOCAL TIPS EXTRACTION PROMPT
# ============================================================================

LOCAL_TIPS_PROMPT = """You are a local knowledge extraction specialist. Extract practical tips and local information from the provided HTML or text and return it as JSON.

**Instructions:**
1. Extract ONLY information explicitly stated in the source text
2. For each field, include an "evidence" field showing where you found the information
3. Use null for any field not found in the source
4. Normalize all data
5. DO NOT invent or assume information

**Required Output Format:**
```json
{{
  "tip_title": "string or null",
  "tip_title_evidence": "exact quote from source",
  "category": "safety|money|transportation|culture|weather|health|general or null",
  "category_evidence": "exact quote from source",
  "location": "string or null",
  "location_evidence": "exact quote from source",
  "description": "string or null - EXTRACT THE COMPLETE AND FULL DESCRIPTION. Include all contextual information, explanations, and details. DO NOT truncate or summarize - capture the entire descriptive text available.",
  "practical_advice": ["array of specific tips"] or null,
  "advice_evidence": "exact quote from source",
  "cost_estimate": "string or null (e.g., '$10-20 per day')",
  "cost_evidence": "exact quote from source",
  "best_time": "string or null (e.g., 'dry season: December-April')",
  "time_evidence": "exact quote from source",
  "things_to_avoid": ["array of strings"] or null,
  "avoid_evidence": "exact quote from source",
  "local_customs": ["array of strings"] or null,
  "customs_evidence": "exact quote from source",
  "emergency_contacts": {{"police": "string", "ambulance": "string", "etc": "string"}} or null,
  "emergency_evidence": "exact quote from source",
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation of confidence score"
}}
```

Now extract the local tips information from:

---
{content}
---

Return ONLY the JSON object."""


# ============================================================================
# REAL ESTATE GUIDE EXTRACTION PROMPT
# ============================================================================

REAL_ESTATE_GUIDE_PROMPT = """You are a real estate market guide extraction specialist. This appears to be a GENERAL GUIDE page (not a single property), so extract overview information about the real estate market.

**Instructions:**
1. Extract general information about the real estate market and available properties
2. DO NOT try to extract details of a single property (this is a guide/listing page)
3. Focus on: destination, market overview, property types, price ranges, popular areas
4. Use null for any field not found in the source

**Required Output Format:**
```json
{{
  "page_type": "general_guide",
  "destination": "string (e.g., 'Costa Rica Real Estate', 'Guanacaste Properties')",
  "destination_evidence": "exact quote",
  "overview": "string (general description of the real estate market)",
  "overview_evidence": "exact quote",
  "property_types_available": ["condo", "house", "land", "commercial", "farm", "etc"],
  "types_evidence": "exact quote",
  "price_range": {{
    "min_usd": number or null,
    "max_usd": number or null,
    "typical_usd": number or null
  }},
  "price_range_evidence": "exact quote",
  "popular_areas": ["area 1", "area 2", "etc"],
  "areas_evidence": "exact quote",
  "market_trends": "string or null (description of current market conditions)",
  "trends_evidence": "exact quote",
  "featured_properties": [
    {{
      "name": "property name",
      "price_usd": number or null,
      "type": "string or null",
      "highlight": "string (why it's featured)"
    }}
  ],
  "featured_evidence": "exact quote",
  "total_properties_mentioned": number or null,
  "total_evidence": "exact quote",
  "investment_tips": ["tip 1", "tip 2", "etc"],
  "tips_evidence": "exact quote",
  "legal_considerations": ["consideration 1", "consideration 2", "etc"],
  "legal_evidence": "exact quote",
  "featured_items_count": number or null,
  "extraction_confidence": number (0.0 to 1.0),
  "confidence_reasoning": "brief explanation"
}}
```

Now extract the real estate guide information from:

---
{content}
---

Return ONLY the JSON object."""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_extraction_prompt(content_type: str, is_specific: bool = True) -> str:
    """
    Get the appropriate extraction prompt for a content type.
    
    Args:
        content_type: One of 'tour', 'restaurant', 'real_estate', 'transportation', 'local_tips'
        is_specific: True for specific entity pages, False for general/listing pages
    
    Returns:
        The extraction prompt string
    
    Raises:
        ValueError: If content_type is not supported
    """
    prompts_map = {
        'real_estate': {
            'specific': PROPERTY_EXTRACTION_PROMPT,
            'general': REAL_ESTATE_GUIDE_PROMPT,
        },
        'tour': {
            'specific': TOUR_SPECIFIC_PROMPT,
            'general': TOUR_GENERAL_PROMPT,
        },
        'restaurant': {
            'specific': RESTAURANT_SPECIFIC_PROMPT,
            'general': RESTAURANT_GENERAL_PROMPT,
        },
        'transportation': {
            'specific': TRANSPORTATION_SPECIFIC_PROMPT,
            'general': TRANSPORTATION_GENERAL_PROMPT,
        },
        'local_tips': {
            'specific': LOCAL_TIPS_PROMPT,
            'general': LOCAL_TIPS_PROMPT,  # Same for both
        },
    }
    
    if content_type not in prompts_map:
        raise ValueError(f"Unsupported content type: {content_type}")
    
    page_type = 'specific' if is_specific else 'general'
    return prompts_map[content_type][page_type]


__all__ = [
    'PROPERTY_EXTRACTION_PROMPT',
    'REAL_ESTATE_GUIDE_PROMPT',
    'TOUR_SPECIFIC_PROMPT',
    'TOUR_GENERAL_PROMPT',
    'RESTAURANT_SPECIFIC_PROMPT',
    'RESTAURANT_GENERAL_PROMPT',
    'TRANSPORTATION_SPECIFIC_PROMPT',
    'TRANSPORTATION_GENERAL_PROMPT',
    'LOCAL_TIPS_PROMPT',
    'get_extraction_prompt',
]
