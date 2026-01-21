"""
LLM-powered property extraction from HTML/text.
"""

import json
import logging
from typing import Dict, Optional
from decimal import Decimal

import openai
from django.conf import settings
from django.utils import timezone

from ..content_types import get_extraction_prompt, CONTENT_TYPES, get_allowed_fields
from .web_search import get_web_search_service

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass


class PropertyExtractor:
    """
    Extract structured data from unstructured HTML/text using LLM.
    Supports multiple content types: real_estate, tour, restaurant, local_tips, transportation.
    """
    
    def __init__(self, content_type: str = 'real_estate', page_type: str = 'specific'):
        """
        Initialize extractor.
        
        Args:
            content_type: Type of content to extract (real_estate, tour, restaurant, etc.)
            page_type: Type of page ('specific' for single item, 'general' for guides/listings)
        """
        api_key = settings.OPENAI_API_KEY
        logger.info(f"🔑 OPENAI_API_KEY configured: {'Yes' if api_key else 'No'}")
        logger.info(f"🔑 API Key length: {len(api_key) if api_key else 0} chars")
        logger.info(f"🔑 API Key preview: {api_key[:10]}..." if api_key and len(api_key) > 10 else "🔑 API Key: EMPTY or TOO SHORT")
        
        if not api_key:
            logger.error("❌ OPENAI_API_KEY is empty! Check environment variables.")
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Validate content type
        if content_type not in CONTENT_TYPES:
            logger.warning(f"⚠️ Unknown content type: {content_type}, defaulting to real_estate")
            content_type = 'real_estate'
        
        # Validate page type
        if page_type not in ['specific', 'general']:
            logger.warning(f"⚠️ Unknown page type: {page_type}, defaulting to specific")
            page_type = 'specific'
        
        self.content_type = content_type
        self.page_type = page_type
        self.client = openai.OpenAI(api_key=api_key)
        self.model = settings.OPENAI_MODEL_CHAT
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = 0.1  # Low temperature for consistent extraction
        
        logger.info(f"📝 Extractor initialized for content type: {content_type}, page type: {page_type}")
    
    def _clean_content(self, content: str) -> str:
        """Clean and truncate content for LLM processing."""
        from bs4 import BeautifulSoup
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract key sections
        important_text = []
        
        # 1. Title and meta description
        title = soup.find('title')
        if title:
            important_text.append(f"TITLE: {title.get_text(strip=True)}")
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            important_text.append(f"META DESCRIPTION: {meta_desc['content']}")
        
        # 2. ALL headings (h1-h6) - often contain key info like prices, features, sections
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings = soup.find_all(heading_tag)
            for heading in headings:
                text = heading.get_text(strip=True)
                if text and len(text) > 2:
                    important_text.append(f"HEADING ({heading_tag.upper()}): {text}")
        
        # 3. Property details sections (common patterns)
        detail_patterns = [
            {'class': lambda x: x and any(word in str(x).lower() for word in 
                ['show__', 'product', 'detail', 'property', 'tour', 'rate', 'price', 'cost', 'schedule', 'info', 'feature', 'highlight'])},
            {'id': lambda x: x and any(word in x.lower() for word in 
                ['detail', 'overview', 'price', 'rate', 'schedule', 'info', 'description', 'feature'])},
        ]
        
        for pattern in detail_patterns:
            elements = soup.find_all('div', **pattern)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 10:  # Skip very short snippets
                    important_text.append(f"SECTION: {text[:500]}")  # Limit each section to 500 chars
        
        # 4. Structured data (JSON-LD, microdata) - VERY IMPORTANT
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                important_text.append(f"STRUCTURED DATA: {script.string}")
        
        # 4b. Extract JSON from regular script tags (for TripAdvisor, etc.)
        import json
        import re
        all_scripts = soup.find_all('script')
        for script in all_scripts:
            if script.string and len(script.string) > 100:  # Only process substantial scripts
                # Look for JSON objects in the script
                json_pattern = r'\{[^{}]*(?:"[^"]*"[^{}]*)*\}'
                matches = re.findall(json_pattern, script.string[:5000])  # First 5000 chars only
                for match in matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, dict) and len(parsed) > 2:  # Valid JSON with content
                            important_text.append(f"SCRIPT JSON: {json.dumps(parsed)[:1000]}")
                    except:
                        pass  # Not valid JSON, skip
        
        # 4c. Extract data from data-* attributes
        all_tags = soup.find_all(attrs={'data-details': True})
        for tag in all_tags:
            for attr_name, attr_value in tag.attrs.items():
                if attr_name.startswith('data-') and len(str(attr_value)) > 20:
                    important_text.append(f"DATA ATTRIBUTE ({attr_name}): {attr_value}")
        
        # 5. Lists (ul, ol) - often contain features, inclusions, schedules
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = list_elem.find_all('li')
            if items and len(items) > 1:  # Only capture lists with multiple items
                list_text = ' | '.join([item.get_text(strip=True) for item in items[:10]])  # Max 10 items
                if len(list_text) > 20:
                    important_text.append(f"LIST: {list_text}")
        
        # 6. Description/content paragraphs (LIMIT TO FIRST 20 for efficiency)
        paragraphs = soup.find_all('p')
        for idx, p in enumerate(paragraphs):
            if idx >= 20:  # Only process first 20 paragraphs
                break
            text = p.get_text(separator=' ', strip=True)
            if len(text) > 50:  # Skip short paragraphs
                important_text.append(f"PARAGRAPH: {text[:300]}")  # Limit to 300 chars
        
        # 7. Tables - often contain pricing, schedules, features
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if rows:
                table_text = ' | '.join([row.get_text(separator=' ', strip=True) for row in rows[:10]])
                if len(table_text) > 20:
                    important_text.append(f"TABLE: {table_text}")
        
        # 8. All remaining text as fallback (if nothing structured found)
        if len(important_text) < 10:
            # If no structured sections found, get all text
            all_text = soup.get_text(separator=' ', strip=True)
            important_text.append(f"FULL TEXT: {all_text}")
        
        # Combine all extracted text
        combined = '\n\n'.join(important_text)
        
        # Remove excessive whitespace
        combined = ' '.join(combined.split())
        
        # Truncate if still too long (max 50K chars to keep prompt under ~15K tokens)
        # This balances thoroughness with API speed/cost
        max_length = 50000
        if len(combined) > max_length:
            combined = combined[:max_length] + "...[truncated]"
        
        return combined
    
    def _fill_missing_fields_with_inference(self, data: Dict, cleaned_content: str, raw_html: str) -> Dict:
        """
        Second pass: Fill missing fields by inferring from full content.
        
        This method analyzes which fields are null after initial extraction,
        then makes a targeted API call to infer/derive those fields from the
        complete content context.
        
        Args:
            data: Initial extraction results
            cleaned_content: Cleaned HTML content
            raw_html: Original HTML
            
        Returns:
            Updated data dictionary with inferred fields
        """
        
        # Define fields that can be inferred for each content type
        inferable_fields_by_type = {
            'tour': [
                'duration_hours', 'difficulty_level', 'included_items', 'excluded_items',
                'max_participants', 'languages_available', 'pickup_included', 
                'minimum_age', 'cancellation_policy', 'schedules', 'what_to_bring',
                'check_in_time', 'restrictions'
            ],
            'restaurant': [
                'opening_hours', 'cuisine_type', 'price_range', 'dress_code',
                'reservation_required', 'parking_available'
            ],
            'transportation': [
                'origin', 'distance_km', 'route_options', 'fastest_option', 
                'cheapest_option', 'recommended_option', 'travel_tips', 
                'things_to_know', 'best_time_to_travel', 'things_to_avoid',
                'accessibility_info'
            ],
            'real_estate': [
                'year_built', 'lot_size_m2', 'hoa_fee_monthly', 'property_tax_annual'
            ]
        }
        
        inferable_fields = inferable_fields_by_type.get(self.content_type, [])
        
        # Find which fields are null
        missing_fields = []
        for field in inferable_fields:
            # Check both property_name and content-specific name (e.g., tour_name)
            if data.get(field) in [None, '', []]:
                missing_fields.append(field)
        
        # If no missing fields or no inferable fields, skip second pass
        if not missing_fields:
            logger.info("✅ All fields filled, skipping inference pass")
            return data
        
        logger.info(f"🔍 Second pass: Inferring {len(missing_fields)} missing fields: {missing_fields}")
        
        # Build inference prompt - DIFFERENT FOR REAL ESTATE vs TOURS
        if self.content_type == 'real_estate':
            inference_prompt = f"""You are an EXPERT real estate analyst specializing in Costa Rican property data.
Your task is to AGGRESSIVELY INFER missing information using ALL available context.

**Already Extracted:**
{json.dumps({k: v for k, v in data.items() if not k.endswith('_evidence') and k not in ['raw_html', 'field_confidence', 'extracted_at', 'tokens_used']}, indent=2, default=str)}

**Missing/Incomplete Fields to Fill:**
{', '.join(missing_fields)}

**Full Content (Raw HTML and Text):**
{cleaned_content}

**AGGRESSIVE INFERENCE INSTRUCTIONS FOR COSTA RICAN REAL ESTATE:**

1. **Property Features Analysis:**
   - Examine ALL text for: bedroom mentions, bathroom counts, pool indicators, parking spots
   - Look for "dormitorios", "habitaciones", "cuartos", "baños", "garaje", "estacionamiento"
   - If land type: infer "0" bedrooms and bathrooms
   - For size/area: look for "m²", "metros", "lote de", "terreno de" patterns

2. **Amenities Extraction:**
   - Search for ALL indicators: pool, garden, patio, deck, security, gate, garage
   - Spanish: piscina, jardín, terraza, cerca, portón, cochera, bodega, aire acondicionado
   - Extract as comprehensive list

3. **Area and Lot Size Inference:**
   - Land in Costa Rica typically: 100m² to 10,000m² (0.01 to 1 hectare)
   - Curridabat: premium suburban area, plots often 500-2000m²
   - URL hints: "land-for-sale" confirms terreno/lote

4. **Description Inference:**
   - Combine: property type + location + price + amenities -> create realistic description
   - Example: "Exclusive land plot in Curridabat, prime investment opportunity with development potential"

5. **Field-Specific Rules:**
   - **bedrooms**: Land=0, if missing & residential=infer 2-3
   - **bathrooms**: Land=0, if missing & residential=infer 1-2
   - **area_sqm**: Critical field, look for all number patterns
   - **lot_size_sqm**: For land, often same as area_sqm
   - **parking_spaces**: Land=0, residential=infer 1-2
   - **amenities**: Always extract something based on context
   - **property_condition**: High price -> "Excellent", Standard -> "Good"

**Output Format - ONLY JSON:**
```json
{{
  "bedrooms": <number or null>,
  "bathrooms": <number or null>,
  "area_sqm": <number or null>,
  "lot_size_sqm": <number or null>,
  "parking_spaces": <number or null>,
  "amenities": <list or null>,
  "property_condition": <string or null>,
  "description": <detailed string or null>
}}
```

**CRITICAL:** Return numbers not strings. For land: bedrooms=0, bathrooms=0, parking_spaces=0"""
        
        elif self.content_type == 'transportation':
            # TRANSPORTATION-SPECIFIC INFERENCE PROMPT
            inference_prompt = f"""Eres un experto en análisis de información de transporte. Debes INFERIR agresivamente los campos faltantes usando TODO el contexto disponible.

**Datos ya extraídos:**
{json.dumps({k: v for k, v in data.items() if not k.endswith('_evidence') and k not in ['raw_html', 'field_confidence', 'extracted_at', 'tokens_used']}, indent=2, default=str, ensure_ascii=False)}

**Campos faltantes a inferir:**
{', '.join(missing_fields)}

**Contenido completo:**
{cleaned_content[:15000]}

**INSTRUCCIONES DE INFERENCIA AGRESIVA:**

1. **origin (punto de partida):**
   - Busca menciones de aeropuertos, ciudades, hoteles de origen
   - Palabras clave: "from", "desde", "salida de", "departure from"
   - Si hay URL con nombres de lugares, usa el primero como origen

2. **distance_km (distancia en kilómetros):**
   - Busca números + "km", "kilometers", "kilómetros", "miles"
   - Convierte millas a km (1 mile = 1.6 km)
   - Si dice "1 hour drive" sin km, infiere ~60-80km

3. **route_options (opciones de ruta):**
   - Extrae TODAS las menciones de: bus, taxi, shuttle, car rental, private transfer, Uber
   - Busca precios ($, USD, colones), duraciones (hours, mins)
   - Formato: [{{"transport_type": "...", "price_usd": X, "duration_hours": Y, "description": "..."}}]

4. **fastest_option / cheapest_option / recommended_option:**
   - Analiza tiempos mencionados → fastest
   - Analiza precios → cheapest
   - Busca palabras "recommended", "best", "most popular" → recommended
   - Formato: {{"transport_type": "...", "reason": "..."}}

5. **travel_tips (consejos de viaje):**
   - Extrae tips prácticos mencionados
   - Busca: "tip", "advice", "recommendation", "should know"
   - Lista completa de frases útiles

6. **things_to_know (cosas a saber):**
   - Información importante: horarios, frecuencias, reservas necesarias
   - Restricciones, requisitos, documentos
   - Clima, temporada, condiciones de rutas

7. **best_time_to_travel (mejor momento):**
   - Busca menciones de horarios recomendados
   - Temporadas (dry season, rainy season)
   - Horarios de menor tráfico

8. **things_to_avoid (cosas a evitar):**
   - Advertencias, riesgos, problemas comunes
   - "avoid", "don't", "not recommended"
   - Horarios pico, rutas peligrosas

9. **accessibility_info (accesibilidad):**
   - Menciones de wheelchair, disabled access, elderly-friendly
   - "accessible", "accesible", "adaptado"

**REGLAS CRÍTICAS:**
- TODO debe estar en ESPAÑOL (traduce si es necesario)
- Si un campo NO puede inferirse del contenido → null
- Para listas vacías → []
- Para route_options: extrae TODAS las opciones mencionadas, con precios/duraciones si están disponibles
- Números como números, no strings

**Formato de salida - SOLO JSON:**
```json
{{
  "origin": <string o null>,
  "distance_km": <number o null>,
  "route_options": [
    {{
      "transport_type": "tipo de transporte",
      "transport_name": "nombre del servicio (opcional)",
      "price_usd": <number o null>,
      "duration_hours": <number o null>,
      "description": "descripción completa"
    }}
  ],
  "fastest_option": {{"transport_type": "...", "reason": "..."}},
  "cheapest_option": {{"transport_type": "...", "reason": "..."}},
  "recommended_option": {{"transport_type": "...", "reason": "..."}},
  "travel_tips": ["tip1", "tip2", ...],
  "things_to_know": ["info1", "info2", ...],
  "best_time_to_travel": <string o null>,
  "things_to_avoid": ["cosa1", "cosa2", ...],
  "accessibility_info": <string o null>
}}
```

Infiere los campos faltantes ahora:"""
        
        else:
            # ORIGINAL PROMPT FOR TOURS AND OTHER CONTENT TYPES
            inference_prompt = f"""You are analyzing a {self.content_type} page to fill in missing information.

**Already Extracted:**
{json.dumps({k: v for k, v in data.items() if not k.endswith('_evidence') and k not in ['raw_html', 'field_confidence', 'extracted_at', 'tokens_used']}, indent=2, default=str)}

**Missing Fields to Infer:**
{', '.join(missing_fields)}

**Full Content:**
{cleaned_content}

**Instructions:**
1. Analyze the full content carefully
2. For each missing field, try to INFER or DERIVE the information from context
3. Look for implicit information, schedules, lists, restrictions, tips
4. If a field truly cannot be inferred, return null
5. Return ONLY valid JSON with the missing fields

**Output Format:**
```json
{{
  "duration_hours": <inferred value or null>,
  "schedules": <inferred value or null>,
  "minimum_age": <inferred value or null>,
  "what_to_bring": <inferred list or null>,
  "check_in_time": <inferred value or null>,
  "restrictions": <inferred list or null>,
  ... (only fields that were missing)
}}
```

**Examples of Inference:**
- If content says "Child rates apply from ages 5 to 12" -> minimum_age: 5
- If content says "8:00am | 9:00am | 10:30am" -> schedules: ["08:00", "09:00", "10:30"]
- If content says "Wear comfortable clothes, sunscreen" -> what_to_bring: ["comfortable clothes", "sunscreen", ...]
- If content says "Check-in 15 minutes prior" -> check_in_time: "15 minutes before tour"

Now infer the missing fields:"""

        try:
            logger.info("🤖 Calling OpenAI for inference...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at inferring information from context. Output only valid JSON."},
                    {"role": "user", "content": inference_prompt}
                ],
                temperature=0.3,  # Lower temperature for more factual inference
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            inferred_json = response.choices[0].message.content
            inferred_data = json.loads(inferred_json)
            
            logger.info(f"✅ Inferred {len(inferred_data)} fields")
            logger.info(f"Inferred data: {json.dumps(inferred_data, indent=2, default=str)[:500]}")
            
            # Update tokens used
            data['tokens_used'] = data.get('tokens_used', 0) + response.usage.total_tokens
            
            # Merge inferred data into main data
            filled_count = 0
            for field, value in inferred_data.items():
                if value not in [None, '', []]:
                    data[field] = value
                    filled_count += 1
                    logger.info(f"  ✅ Filled {field}: {value}")
            
            logger.info(f"🎯 Second pass filled {filled_count}/{len(missing_fields)} fields")
            
            # THIRD PASS - ONLY FOR REAL ESTATE: Ultra-aggressive inference
            if self.content_type == 'real_estate':
                still_missing = [f for f in missing_fields if data.get(f) in [None, '', 'N/A', []]]
                if still_missing:
                    logger.info(f"🔥 THIRD PASS (Real Estate Only): Ultra-aggressive inference for {len(still_missing)} remaining fields")
                    
                    third_pass_prompt = f"""You are a Costa Rican real estate EXPERT. Fill remaining critical gaps with aggressive inference.

Current Property Data:
{json.dumps({k: v for k, v in data.items() if k in ['property_name', 'price_usd', 'location', 'area_sqm', 'lot_size_sqm', 'property_type']}, indent=2, default=str)}

Still Missing/Empty: {', '.join(still_missing)}

Full Content:
{cleaned_content}

ULTRA-AGGRESSIVE INFERENCE FOR COSTA RICA REAL ESTATE:
1. Land properties (lote/terreno): bedrooms=0, bathrooms=0, parking_spaces=0
2. No description? Create one: "{data.get('property_name', 'Property')} in {data.get('location', 'Costa Rica')}, listed at ${data.get('price_usd', 'price')} USD"
3. No amenities? Infer from land: ["Level land", "Access road", "Development potential"] or similar
4. Curridabat location: "Excellent" condition, premium area
5. Large area (>5000m²): "Development opportunity" or "Multi-unit potential"

Return ONLY JSON with values or nulls for missing fields."""

                    try:
                        response3 = self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": "You are a Costa Rican real estate expert. Aggressively fill missing fields based on property context. Return only JSON."},
                                {"role": "user", "content": third_pass_prompt}
                            ],
                            temperature=0.5,
                            max_tokens=2000,
                            response_format={"type": "json_object"}
                        )
                        
                        third_pass_data = json.loads(response3.choices[0].message.content)
                        data['tokens_used'] = data.get('tokens_used', 0) + response3.usage.total_tokens
                        
                        third_filled = 0
                        for field, value in third_pass_data.items():
                            if field in still_missing and value not in [None, '', []]:
                                data[field] = value
                                third_filled += 1
                                logger.info(f"  🔥 Third pass filled {field}: {value}")
                        
                        logger.info(f"🔥 Third pass filled {third_filled}/{len(still_missing)} fields")
                    except Exception as e:
                        logger.warning(f"⚠️ Third pass failed: {e}")
            
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Inference pass failed: {e}, continuing with original data")
            return data
    
    def _validate_extraction(self, data: Dict) -> Dict:
        """Validate and clean extracted data based on page type."""
        validated = {}
        
        # For GENERAL pages, preserve guide fields without strict validation
        if self.page_type == 'general':
            # Copy all guide-specific fields directly
            guide_fields = [
                'page_type', 'destination', 'overview', 
                'property_types_available', 'tour_types_available',
                'price_range', 'popular_areas', 'market_trends',
                'featured_properties', 'featured_tours', 'featured_items_count',
                'total_properties_mentioned', 'total_tours_mentioned',
                'investment_tips', 'booking_tips', 'legal_considerations',
                'best_season', 'best_time_of_day', 'duration_range',
                'tips', 'things_to_bring', 'cuisine_types',
                # NEW: Extended tour guide fields
                'regions', 'seasonal_activities', 'faqs', 'what_to_pack',
                'family_friendly', 'accessibility_info'
            ]
            
            for field in guide_fields:
                if field in data:
                    validated[field] = data[field]
        
        # ============================================================================
        # FIELD PRESERVATION: Keep content-type specific field names
        # ============================================================================
        # Instead of mapping tour_name -> property_name, we keep both:
        # - tour_name, restaurant_name, etc. (original specific fields)
        # - property_name (copy for DB compatibility)
        #
        # This allows frontend to display context-appropriate labels while
        # maintaining backward compatibility with Property model.
        
        field_mapping = {
            'tour': {
                'tour_name': 'property_name',
                'tour_type': 'property_type',
            },
            'restaurant': {
                'restaurant_name': 'property_name',
                'cuisine_type': 'property_type',
            },
            'real_estate': {
                # Real estate uses property_name/property_type directly (no mapping needed)
            },
            'local_tips': {
                'tip_title': 'property_name',
                'tip_category': 'property_type',
            },
            'transportation': {
                'service_name': 'property_name',
                'transport_type': 'property_type',
            }
        }
        
        # Apply content-type specific mapping (CREATE copies, don't replace)
        content_mapping = field_mapping.get(self.content_type, {})
        for source_field, target_field in content_mapping.items():
            if source_field in data and data[source_field] not in [None, '']:
                # Copy source to target (keep both fields)
                data[target_field] = data[source_field]
                logger.info(f"🔄 Copied {source_field} -> {target_field}: {data[source_field]}")
        
        # For SPECIFIC pages OR common fields, validate property fields
        # Handle price
        if data.get('price_usd'):
            try:
                validated['price_usd'] = Decimal(str(data['price_usd']))
            except (ValueError, TypeError):
                validated['price_usd'] = None
        
        # Handle price_details (JSONField)
        if data.get('price_details'):
            try:
                validated['price_details'] = data['price_details']
                logger.info(f"💰 Saving price_details: {data['price_details']}")
            except Exception as e:
                logger.warning(f"Failed to save price_details: {e}")
                validated['price_details'] = {}
        
        # Handle integers
        for field in ['bedrooms', 'year_built', 'parking_spaces']:
            if data.get(field):
                try:
                    validated[field] = int(data[field])
                except (ValueError, TypeError):
                    validated[field] = None
        
        # Handle decimals
        for field in ['bathrooms', 'square_meters', 'lot_size_m2', 
                     'hoa_fee_monthly', 'property_tax_annual', 'latitude', 'longitude']:
            if data.get(field):
                try:
                    validated[field] = Decimal(str(data[field]))
                except (ValueError, TypeError):
                    validated[field] = None
        
        # Handle strings - BOTH generic and content-specific fields
        generic_fields = ['property_name', 'property_type', 'location', 'description',
                         'listing_id', 'internal_property_id', 'listing_status']
        
        # Get content-specific fields from new modular config
        try:
            content_specific = get_allowed_fields(self.content_type)
        except ValueError:
            # Fallback for unknown content types
            logger.warning(f"Unknown content type '{self.content_type}', using empty field list")
            content_specific = []
        
        # Add content-specific fields for this content type
        all_fields = generic_fields + content_specific
        
        for field in all_fields:
            if field in data:
                validated[field] = data.get(field)
        
        # Handle date_listed
        if data.get('date_listed'):
            validated['date_listed'] = data.get('date_listed')  # Keep as string for now, Django will parse
        else:
            validated['date_listed'] = None
        
        # Handle amenities array
        amenities = data.get('amenities')
        if amenities and isinstance(amenities, list):
            validated['amenities'] = [str(a) for a in amenities]
        else:
            validated['amenities'] = []
        
        # Handle confidence
        try:
            confidence = float(data.get('extraction_confidence', 0.5))
            validated['extraction_confidence'] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            validated['extraction_confidence'] = 0.5
        
        # Store field-level evidence
        evidence_fields = {}
        for key, value in data.items():
            if key.endswith('_evidence'):
                field_name = key.replace('_evidence', '')
                evidence_fields[field_name] = value
        
        validated['field_confidence'] = evidence_fields
        validated['extracted_at'] = timezone.now()
        
        return validated
    
    def _extract_structured_data(self, html: str) -> Dict:
        """
        Pre-parse JSON-LD and structured data from HTML before LLM extraction.
        This is more reliable than asking LLM to parse JSON strings.
        
        Returns:
            Dictionary with pre-extracted structured data
        """
        from bs4 import BeautifulSoup
        import json as json_lib
        
        soup = BeautifulSoup(html, 'html.parser')
        structured_data = {}
        
        # Extract JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                try:
                    data = json_lib.loads(script.string)
                    
                    # For TripAdvisor Restaurant/FoodEstablishment schema
                    if isinstance(data, dict) and data.get('@type') in ['Restaurant', 'FoodEstablishment']:
                        # Extract rating
                        if 'aggregateRating' in data:
                            rating_data = data['aggregateRating']
                            structured_data['rating'] = rating_data.get('ratingValue')
                            structured_data['number_of_reviews'] = rating_data.get('reviewCount')
                        
                        # Extract phone
                        if 'telephone' in data:
                            structured_data['contact_phone'] = data['telephone']
                        
                        # Extract cuisine
                        if 'servesCuisine' in data:
                            cuisine = data['servesCuisine']
                            if isinstance(cuisine, list):
                                structured_data['cuisine_type'] = ', '.join(cuisine)
                            else:
                                structured_data['cuisine_type'] = cuisine
                        
                        # Extract address
                        if 'address' in data:
                            addr = data['address']
                            if isinstance(addr, dict):
                                street = addr.get('streetAddress', '')
                                city = addr.get('addressLocality', '')
                                postal = addr.get('postalCode', '')
                                structured_data['location'] = f"{street}, {city}, {addr.get('addressCountry', {}).get('name', 'CR')} {postal}".strip()
                        
                        # Extract price range
                        if 'priceRange' in data:
                            price_range = data['priceRange']
                            if '$$$$' in price_range:
                                structured_data['price_range'] = 'fine_dining'
                            elif '$$$' in price_range:
                                structured_data['price_range'] = 'upscale'
                            elif '$$' in price_range:
                                structured_data['price_range'] = 'moderate'
                            elif '$' in price_range:
                                structured_data['price_range'] = 'budget'
                        
                        # Extract reservation info
                        if 'acceptsReservations' in data:
                            structured_data['reservation_required'] = data['acceptsReservations']
                        
                        logger.info(f"📊 Pre-extracted {len(structured_data)} fields from JSON-LD: {list(structured_data.keys())}")
                
                except Exception as e:
                    logger.warning(f"Failed to parse JSON-LD: {e}")
                    continue
        
        return structured_data
    
    def extract_from_html(self, html: str, url: Optional[str] = None) -> Dict:
        """
        Extract data from HTML content based on content type.
        
        Args:
            html: HTML content to extract from
            url: Optional source URL
            
        Returns:
            Dictionary with extracted data (fields depend on content_type)
            
        Raises:
            ExtractionError: If extraction fails
        """
        
        # Pre-extract structured data (JSON-LD, schema.org)
        pre_extracted = self._extract_structured_data(html)
        
        # Clean content
        content = self._clean_content(html)
        
        # Get the appropriate prompt for this content type and page type
        extraction_prompt_template = get_extraction_prompt(self.content_type, self.page_type)
        # Use replace instead of format to avoid issues with braces in HTML content
        prompt = extraction_prompt_template.replace('{content}', content)
        
        logger.info(f"Prompt preview (first 800 chars): {prompt[:800]}")
        logger.info(f"Prompt preview (last 800 chars): {prompt[-800:]}")
        
        try:
            logger.info("Starting LLM property extraction...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data extraction specialist that outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Extract JSON from response
            raw_json = response.choices[0].message.content
            
            logger.info(f"LLM extraction completed. Tokens used: {response.usage.total_tokens}")
            logger.info(f"Raw LLM response: {raw_json[:500]}")  # Log first 500 chars
            
            # Parse JSON
            try:
                extracted_data = json.loads(raw_json)
                logger.info(f"Parsed JSON keys: {list(extracted_data.keys())}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                logger.error(f"Raw response was: {raw_json}")
                raise ExtractionError("LLM returned invalid JSON")
            
            # Merge pre-extracted structured data with LLM extraction
            # Pre-extracted data takes precedence for fields where LLM returned null
            logger.info(f"🔄 Merging {len(pre_extracted)} pre-extracted fields...")
            for key, value in pre_extracted.items():
                llm_value = extracted_data.get(key)
                logger.info(f"   {key}: LLM={llm_value}, Pre-extracted={value}")
                if value and llm_value in [None, '', []]:
                    extracted_data[key] = value
                    logger.info(f"   ✅ Using pre-extracted {key}: {value}")
                else:
                    logger.info(f"   ⏭️ Skipping {key} (LLM already has value: {llm_value})")
            
            # Validate and clean
            validated_data = self._validate_extraction(extracted_data)
            
            # ========================================================================
            # SECOND PASS: Fill missing fields with inference from full content
            # ========================================================================
            # If key fields are still null, make a second API call with full context
            # to infer/derive missing information
            validated_data = self._fill_missing_fields_with_inference(
                validated_data, 
                content, 
                html
            )
            
            # ========================================================================
            # THIRD PASS (OPTIONAL): Enrich with web search results
            # ========================================================================
            # Use OpenAI web_search tool to add additional context from live internet
            # This is especially useful for:
            # - Real-time pricing/availability
            # - Reviews and ratings
            # - Updated hours/schedules
            # - Additional details not on scraped page
            web_search_service = get_web_search_service()
            if web_search_service.enabled:
                logger.info("🌐 [WEB SEARCH] Enriching data with web search...")
                validated_data = web_search_service.enrich_property_data(
                    property_data=validated_data,
                    url=url,
                    content_type=self.content_type
                )
            else:
                logger.info("⚠️ [WEB SEARCH] Skipping web search (disabled)")
            
            # Add metadata
            validated_data['source_url'] = url
            validated_data['raw_html'] = html[:10000]  # Store first 10K chars
            validated_data['tokens_used'] = response.usage.total_tokens
            validated_data['content_type'] = self.content_type
            validated_data['page_type'] = self.page_type
            
            logger.info(f"Extraction successful. Confidence: {validated_data['extraction_confidence']}")
            
            return validated_data
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ExtractionError(f"LLM API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected extraction error: {e}")
            raise ExtractionError(f"Extraction failed: {str(e)}")
    
    def extract_from_text(self, text: str) -> Dict:
        """
        Extract property data from plain text.
        
        Args:
            text: Text content to extract from
            
        Returns:
            Dictionary with extracted property data
        """
        return self.extract_from_html(text, url=None)
    
    def extract_with_retry(self, content: str, max_retries: int = 2) -> Dict:
        """
        Extract with retry logic on failure.
        
        Args:
            content: Content to extract from
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with extracted property data
            
        Raises:
            ExtractionError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return self.extract_from_html(content)
            except ExtractionError as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"Extraction attempt {attempt + 1} failed, retrying...")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All {max_retries + 1} extraction attempts failed")
        
        raise last_error


def extract_property_data(content: str, url: Optional[str] = None) -> Dict:
    """
    Convenience function to extract property data.
    
    Usage:
        data = extract_property_data(html_content, url='https://...')
        property_name = data['property_name']
        price = data['price_usd']
    """
    extractor = PropertyExtractor(content_type='real_estate')
    return extractor.extract_from_html(content, url=url)


def extract_content_data(content: str, content_type: str, page_type: str = 'specific', url: Optional[str] = None) -> Dict:
    """
    Generic function to extract data for any content type.
    
    Args:
        content: HTML or text content to extract from
        content_type: Type of content (real_estate, tour, restaurant, local_tips, transportation)
        page_type: Type of page ('specific' for single item details, 'general' for guides/listings)
        url: Optional source URL
        
    Returns:
        Dictionary with extracted data (fields depend on content_type and page_type)
        
    Usage:
        # Extract specific tour data
        data = extract_content_data(html, 'tour', 'specific', url='https://viator.com/tours/d742-12345')
        
        # Extract general tour guide
        data = extract_content_data(html, 'tour', 'general', url='https://costarica.org/tours/')
        
        # Extract restaurant data  
        data = extract_content_data(html, 'restaurant', 'specific', url='https://yelp.com/biz/...')
    """
    extractor = PropertyExtractor(content_type=content_type, page_type=page_type)
    return extractor.extract_from_html(content, url=url)
