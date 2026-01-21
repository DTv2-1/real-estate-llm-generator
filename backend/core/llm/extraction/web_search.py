"""
OpenAI Web Search integration for additional context gathering.
Uses the new Responses API with web_search tool.
"""

import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for performing web searches using OpenAI's web_search tool."""
    
    def __init__(self):
        """Initialize the web search service."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.enabled = getattr(settings, 'WEB_SEARCH_ENABLED', False)
        
        if self.enabled:
            logger.info("🌐 Web Search enabled via OpenAI Responses API")
        else:
            logger.info("⚠️ Web Search disabled - set WEB_SEARCH_ENABLED=True to enable")
    
    def search(
        self,
        query: str,
        model: str = "gpt-4o",
        allowed_domains: Optional[List[str]] = None,
        country: str = "CR",
        max_results: int = 5
    ) -> Dict:
        """
        Perform a web search using OpenAI's web_search tool.
        
        Args:
            query: Search query
            model: Model to use (gpt-4o, gpt-5, o4-mini, etc.)
            allowed_domains: Optional list of domains to restrict search to
            country: Two-letter ISO country code (default: CR for Costa Rica)
            max_results: Maximum number of results to return
            
        Returns:
            Dict with:
                - answer: Text response with inline citations
                - sources: List of URLs consulted
                - citations: List of cited URLs with titles
        """
        if not self.enabled:
            logger.warning("⚠️ Web search called but disabled")
            return {
                'answer': None,
                'sources': [],
                'citations': [],
                'error': 'Web search is disabled'
            }
        
        try:
            logger.info(f"🔍 [WEB SEARCH] Query: {query}")
            logger.info(f"🔍 [WEB SEARCH] Model: {model}")
            logger.info(f"🔍 [WEB SEARCH] Country: {country}")
            
            # Configure web search tool
            tools = [{
                "type": "web_search"
            }]
            
            # Add domain filtering if specified
            if allowed_domains:
                tools[0]["filters"] = {
                    "allowed_domains": allowed_domains
                }
                logger.info(f"🔍 [WEB SEARCH] Restricted to domains: {allowed_domains}")
            
            # Make API call using Responses API
            response = self.client.responses.create(
                model=model,
                tools=tools,
                tool_choice="auto",
                input=query,
                include=["web_search_call.action.sources"]  # Include sources
            )
            
            logger.info(f"✅ [WEB SEARCH] Search completed")
            logger.info(f"🔍 [WEB SEARCH] Response type: {type(response)}")
            logger.info(f"🔍 [WEB SEARCH] Response attributes: {dir(response)}")
            
            # Extract answer text from output
            answer = None
            sources = []
            citations = []
            
            # Response structure is different - let's explore it
            if hasattr(response, 'output'):
                logger.info(f"🔍 [WEB SEARCH] Output type: {type(response.output)}")
                
                # Output is a list of response items
                for item in response.output:
                    logger.info(f"🔍 [WEB SEARCH] Item type: {type(item)}, Item: {item}")
                    
                    # Web search call contains sources
                    if hasattr(item, 'type') and item.type == 'web_search_call':
                        if hasattr(item, 'action') and hasattr(item.action, 'sources'):
                            sources = item.action.sources
                            logger.info(f"📚 [WEB SEARCH] Found {len(sources)} sources")
                    
                    # Message contains the actual answer
                    if hasattr(item, 'type') and item.type == 'message':
                        if hasattr(item, 'content'):
                            # Content is a list of content items
                            for content_item in item.content:
                                if hasattr(content_item, 'text'):
                                    answer = content_item.text
                                    logger.info(f"📝 [WEB SEARCH] Found answer: {answer[:100]}...")
                                
                                # Extract citations if present
                                if hasattr(content_item, 'annotations'):
                                    for annotation in content_item.annotations:
                                        if hasattr(annotation, 'type') and annotation.type == 'url_citation':
                                            citations.append({
                                                'url': getattr(annotation, 'url', None),
                                                'title': getattr(annotation, 'title', None),
                                                'start_index': getattr(annotation, 'start_index', None),
                                                'end_index': getattr(annotation, 'end_index', None)
                                            })
            
            logger.info(f"📊 [WEB SEARCH] Found {len(sources)} sources, {len(citations)} citations")
            
            # Convert sources to serializable format (extract URLs)
            serializable_sources = [str(s.url) if hasattr(s, 'url') else str(s) for s in sources]
            
            return {
                'answer': answer,
                'sources': serializable_sources,
                'citations': citations,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ [WEB SEARCH] Error: {e}")
            return {
                'answer': None,
                'sources': [],
                'citations': [],
                'error': str(e),
                'success': False
            }
    
    def detect_content_type(self, url: str, html_preview: str = None) -> Dict:
        """
        Use web search to detect the content type of a URL.
        
        This is faster and more accurate than the hybrid detection system
        (domain matching + keyword analysis + optional LLM).
        
        Args:
            url: URL to analyze
            html_preview: Optional preview of HTML content (first 2000 chars)
            
        Returns:
            Dict with:
                - content_type: Detected type (real_estate, tour, restaurant, etc.)
                - confidence: Confidence score (0.0-1.0)
                - reasoning: Explanation of detection
                - sources: URLs consulted for detection
        """
        if not self.enabled:
            logger.warning("⚠️ Web search disabled, cannot detect content type")
            return {
                'content_type': 'unknown',
                'confidence': 0.0,
                'reasoning': 'Web search is disabled',
                'sources': []
            }
        
        try:
            # Build simpler detection query focused on URL analysis
            # Don't ask it to analyze, just search for info about the URL
            query = f"What is {url} about? What type of business or content?"
            
            logger.info(f"🔍 [DETECT] Searching for: {query}")
            
            # Perform web search to get context about the URL
            search_result = self.search(
                query=query,
                model="gpt-4o",
                country="CR"
            )
            
            if not search_result['success']:
                return {
                    'content_type': 'unknown',
                    'confidence': 0.0,
                    'reasoning': f"Web search failed: {search_result.get('error')}",
                    'sources': []
                }
            
            answer = search_result['answer']
            
            # Use GPT-4o-mini to classify the content based on web search results
            classification_prompt = f"""Based on the following web search results about a URL, classify the content type.

Web search answer:
{answer}

Classify into ONE of these categories:
- real_estate: Properties for sale/rent, real estate listings
- tour: Tours, activities, attractions, excursions, surf schools, adventure activities
- transportation: Transportation guides, how to get there, routes, transfers
- restaurant: Restaurants, dining, food establishments
- accommodation: Hotels, lodges, resorts, hostels
- local_tips: Travel guides, general tourism information, destination guides
- general: Other content that doesn't fit above categories

Respond with ONLY a JSON object in this exact format:
{{"content_type": "category_name", "confidence": 0.95, "reasoning": "brief explanation"}}"""

            logger.info(f"🤖 [CLASSIFY] Using GPT-4o-mini to classify content...")
            
            # Call GPT-4o-mini for classification
            try:
                classification_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a content classification expert. Respond only with valid JSON."},
                        {"role": "user", "content": classification_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=150
                )
                
                classification_text = classification_response.choices[0].message.content.strip()
                logger.info(f"📝 [CLASSIFY] Raw response: {classification_text}")
                
                # Parse JSON response
                import json
                classification = json.loads(classification_text)
                
                content_type = classification.get('content_type', 'unknown')
                confidence = float(classification.get('confidence', 0.7))
                reasoning = classification.get('reasoning', answer[:200])
                
                logger.info(f"✅ [CLASSIFY] Classified as: {content_type} (confidence: {confidence})")
                
            except Exception as e:
                logger.error(f"❌ [CLASSIFY] Error parsing classification: {e}")
                # Fallback to basic detection
                content_type = 'general'
                confidence = 0.60
                reasoning = answer[:200]
            
            logger.info(f"✅ [DETECT] Detected: {content_type} (confidence: {confidence})")
            logger.info(f"📝 [DETECT] Reasoning: {reasoning[:200]}...")
            
            return {
                'content_type': content_type,
                'confidence': confidence,
                'reasoning': answer,
                'sources': search_result['sources']  # Already converted to strings in search()
            }
            
        except Exception as e:
            logger.error(f"❌ [DETECT] Error detecting content type: {e}")
            import traceback
            traceback.print_exc()
            return {
                'content_type': 'unknown',
                'confidence': 0.0,
                'reasoning': f'Error: {str(e)}',
                'sources': []
            }
    
    def enrich_property_data(
        self,
        property_data: Dict,
        url: str,
        content_type: str = 'real_estate'
    ) -> Dict:
        """
        Use web search to enrich property data with additional context.
        Only performs web search if critical fields are missing.
        
        Args:
            property_data: Existing property data
            url: Original property URL
            content_type: Type of content (real_estate, tour, restaurant, etc.)
            
        Returns:
            Enhanced property data with web search results
        """
        if not self.enabled:
            return property_data
        
        try:
            # Define critical fields by content type
            critical_fields = {
                'real_estate': ['description', 'price', 'bedrooms', 'bathrooms'],
                'tour': ['description', 'price_usd', 'duration_hours', 'included_items'],
                'restaurant': ['description', 'price_range', 'signature_dishes', 'amenities', 'atmosphere'],
                'transportation': ['description', 'price_usd', 'duration_hours'],
                'local_tips': ['description', 'practical_advice']
            }
            
            # Check if critical fields are missing
            fields_to_check = critical_fields.get(content_type, ['description'])
            missing_fields = []
            
            for field in fields_to_check:
                value = property_data.get(field)
                # Consider field missing if null, empty string, empty array, or empty object
                if value is None or value == '' or value == [] or value == {}:
                    missing_fields.append(field)
            
            # ALWAYS run enrichment for local_tips (to capture structured fields)
            # For other content types, only run if critical fields are missing
            if not missing_fields and content_type != 'local_tips':
                logger.info(f"✅ [ENRICH] All critical fields populated, skipping web search")
                return property_data
            
            if content_type == 'local_tips':
                logger.info(f"🔍 [ENRICH] local_tips content - ALWAYS enriching to capture structured fields (destinations, budget, etc.)")
            else:
                logger.info(f"🔍 [ENRICH] Missing fields: {missing_fields}, performing web search...")
            
            # Build search query based on content type
            if content_type == 'real_estate':
                property_name = property_data.get('property_name') or property_data.get('title')
                location = property_data.get('location')
                
                # If basic fields are missing/null, use the URL instead
                if not property_name or not location:
                    query = f"{url} real estate property listings details prices"
                    logger.info(f"🔍 [ENRICH] Using URL-based query (missing name/location)")
                else:
                    query = f"{property_name} {location} real estate reviews ratings"
                
            elif content_type == 'tour':
                tour_name = property_data.get('tour_name') or property_data.get('property_name')
                
                # If tour name is missing, use URL
                if not tour_name:
                    query = f"{url} tour details prices reviews"
                    logger.info(f"🔍 [ENRICH] Using URL-based query (missing tour name)")
                else:
                    query = f"{tour_name} Costa Rica tour reviews prices"
                
            elif content_type == 'restaurant':
                restaurant_name = property_data.get('restaurant_name')
                location = property_data.get('location')
                
                # If restaurant name is missing, use URL
                if not restaurant_name:
                    query = f"{url} restaurant menu prices reviews"
                    logger.info(f"🔍 [ENRICH] Using URL-based query (missing restaurant name)")
                else:
                    # Only include missing fields in query for efficiency
                    search_terms = []
                    if 'description' in missing_fields or 'atmosphere' in missing_fields:
                        search_terms.append('reviews')
                    if 'signature_dishes' in missing_fields:
                        search_terms.append('menu')
                    if 'price_details' in missing_fields:
                        search_terms.append('prices')
                    if 'amenities' in missing_fields or 'special_experiences' in missing_fields:
                        search_terms.append('features')
                    
                    query = f"{restaurant_name} {location} restaurant {' '.join(search_terms or ['reviews'])}"
                
            else:
                query = f"{url} information reviews"
            
            logger.info(f"🔍 [ENRICH] Searching for additional context: {query}")
            
            # Perform web search
            search_result = self.search(
                query=query,
                model="gpt-4o",
                country="CR"
            )
            
            if search_result['success'] and search_result['answer']:
                # Add web search results to property data
                property_data['web_search_context'] = search_result['answer']
                property_data['web_search_sources'] = search_result['sources']
                property_data['web_search_citations'] = search_result['citations']
                
                logger.info(f"✅ [ENRICH] Added web search context to property data")
            
            return property_data
            
        except Exception as e:
            logger.error(f"❌ [ENRICH] Error enriching property data: {e}")
            return property_data
    
    def extract_from_web_context(
        self,
        web_search_context: str,
        existing_data: Dict,
        content_type: str = 'tour',
        page_type: str = 'specific'
    ) -> Dict:
        """
        Extract structured data from web_search_context to fill missing fields.
        
        Args:
            web_search_context: The enrichment text from web search
            existing_data: Already extracted data from HTML
            content_type: Type of content (tour, real_estate, restaurant, etc.)
            page_type: Type of page ('general' for listings, 'specific' for individual entities)
            
        Returns:
            Dictionary with extracted fields from web context
        """
        if not web_search_context:
            return {}
        
        try:
            logger.info(f"🔍 [CONTEXT_EXTRACT] Extracting structured data from web search context ({len(web_search_context)} chars) - Type: {content_type}/{page_type}")
            
            # Build extraction prompt based on content type AND page type
            if content_type == 'tour' and page_type == 'specific':
                extraction_prompt = f"""You are extracting tour information from web search results. Parse the markdown/text and convert to CLEAN structured data for a professional UI.

EXISTING DATA (already extracted from HTML):
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ONLY the MISSING fields (fields that are null/empty in EXISTING DATA) from the web search context.

CRITICAL FORMATTING RULES - NO EXCEPTIONS:

1. **price_usd**: NUMBER ONLY (e.g., 63.45) - Extract LOWEST price, convert JOD to USD (multiply by 1.41)

2. **price_details**: CLEAN TEXT, NO symbols, NO markdown
   ✅ CORRECT: "Gyrocopter from 63 USD, Hot air balloon 183-197 USD, Skydiving 345 USD"
   ❌ WRONG: "$63 USD" or "**Gyrocopter**: $63" or "- Gyrocopter: $63"

3. **duration_hours**: DECIMAL NUMBER (0.33 for 20 min, 1.0 for 60 min, 2.0 for 2 hours)

4. **description**: PLAIN TEXT, 1-2 sentences, NO markdown, NO ** or - or #
   ✅ CORRECT: "Aerial adventure experiences including gyrocopter rides and hot air balloon flights over Jordan."
   ❌ WRONG: "**Aerial** adventure" or "- Gyrocopter rides" or "## Description"

5. **tour_type**: SINGLE WORD: adventure, cultural, nature, wildlife, beach, food, sightseeing, water_sports, aerial

6. **included_items**: ARRAY of SHORT phrases, NO emojis, NO bullets
   ✅ CORRECT: ["safety equipment", "professional guide", "photos", "refreshments"]
   ❌ WRONG: ["✅ equipment", "- guide", "**photos**"]

7. **excluded_items**: ARRAY of SHORT phrases, NO emojis, NO bullets
   ✅ CORRECT: ["meals", "hotel transport", "personal expenses"]
   ❌ WRONG: ["❌ meals", "- transport"]

8. **difficulty_level**: ONE WORD: easy, moderate, challenging

9. **languages_available**: ARRAY like ["English", "Arabic", "Spanish"]

10. **minimum_age**: INTEGER NUMBER (e.g., 12)

11. **max_participants**: INTEGER NUMBER (e.g., 10)

12. **cancellation_policy**: SHORT PLAIN TEXT, NO markdown
    ✅ CORRECT: "Free cancellation 24 hours before departure"
    ❌ WRONG: "**Free** cancellation" or "- Free cancellation"

13. **pickup_included**: BOOLEAN true or false

ABSOLUTELY NO:
- Markdown symbols: ** # - * _
- Emojis: ✅ ❌ 💰 🎯
- Bullet points or lists in text fields
- Currency symbols in text (use "USD" word instead)
- Parentheses with citations
- Formatting codes

CONVERSION:
- JOD to USD: multiply by 1.41
- Minutes to hours: divide by 60 (20 min = 0.33, 30 min = 0.5)

Return ONLY valid JSON. Use null for missing data.
"""

            elif content_type == 'real_estate':
                extraction_prompt = f"""You are extracting real estate listing information from web search results. Parse the text and convert to COMPLETE structured data.

EXISTING DATA (from HTML - mostly empty/null):
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ALL available fields from the web search context to fill the COMPLETE schema. This is a LISTING PAGE, extract:

REQUIRED FIELDS:

1. **search_location**: STRING - Geographic area/city (e.g., "San José, Costa Rica", "Escazú", "Santa Ana")
   Extract from: "listings in San José", "properties in Escazú"

2. **search_filters**: OBJECT
   - property_type: "apartment" | "house" | "lot" | "commercial" | "condo" | null
   - transaction_type: "sale" | "rent" | null  
   - price_min: NUMBER in USD or null
   - price_max: NUMBER in USD or null

3. **total_results**: INTEGER - Total number of properties mentioned

4. **properties**: ARRAY of property objects (extract ALL properties mentioned):
   [
     {{
       "title": "Short descriptive title",
       "price_usd": NUMBER (price in USD),
       "location": "Specific location/neighborhood",
       "bedrooms": INTEGER or 0,
       "bathrooms": INTEGER or 0,
       "area_sqm": NUMBER (convert sq ft to sqm: divide by 10.764) or null,
       "property_type": "apartment|house|lot|commercial|condo",
       "key_features": ["feature1", "feature2", "feature3"]
     }}
   ]

5. **price_range_summary**: OBJECT
   - lowest_usd: NUMBER (lowest price found)
   - highest_usd: NUMBER (highest price found)  
   - average_usd: NUMBER (calculate average)

6. **popular_areas**: ARRAY of STRING - Neighborhoods mentioned (e.g., ["Escazú", "Santa Ana", "Curridabat"])

FORMATTING RULES:

- **Properties array**: Extract EVERY property mentioned with complete data
- **Prices**: Always in USD, clean numbers (385000 not "$385,000")
- **Sizes**: Convert sq ft to sqm (divide by 10.764)
- **Features**: Clean array, NO emojis, NO markdown ["pool", "garden", "parking"]
- **Locations**: Specific neighborhoods/areas within the city
- **Property titles**: Short descriptive text from the web context

CONVERSION EXAMPLES:
- "5,382 sq ft" → 500 sqm (5382 / 10.764)
- "800 m²" → 800 sqm (already in sqm)
- "$471,699" → 471699
- "approximately $385,000" → 385000

Extract ALL properties listed in the context (aim for 10-20+ properties). Return valid JSON."""

            elif content_type == 'tour' and page_type == 'general':
                extraction_prompt = f"""You are extracting tour LISTING/GUIDE information from web search results. This is a GENERAL page with MULTIPLE tours, not a specific tour.

EXISTING DATA (from HTML - mostly empty/null):
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ALL available fields for a tour listing/guide page:

REQUIRED FIELDS:

1. **operator_name**: STRING - Name of tour operator or company
2. **location**: STRING - Main location/destination covered
3. **available_tours**: ARRAY of tour names/titles mentioned
4. **tour_categories**: ARRAY of tour categories (e.g., ["adventure", "cultural", "nature"])
5. **contact_info**: STRING - Phone, email, or contact details
6. **description**: STRING - About the operator or destination

Extract ALL tours mentioned in the context. Return valid JSON with complete data."""

            elif content_type == 'restaurant' and page_type == 'specific':
                # Convert Decimal to float for JSON serialization
                def decimal_to_float(obj):
                    from decimal import Decimal
                    if isinstance(obj, dict):
                        return {k: decimal_to_float(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [decimal_to_float(item) for item in obj]
                    elif isinstance(obj, Decimal):
                        return float(obj)
                    return obj
                
                serializable_data = decimal_to_float(existing_data)
                
                extraction_prompt = f"""You are extracting restaurant information from web search results. Parse the markdown/text and convert to CLEAN structured data.

EXISTING DATA (already extracted from HTML):
{json.dumps(serializable_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ONLY MISSING fields (fields that are null/empty in EXISTING DATA) from the web search context.

CRITICAL FORMATTING RULES:

1. **description**: PLAIN TEXT, 1-2 sentences, NO markdown, NO ** or - or #
   ✅ CORRECT: "Contemporary Latin-international cuisine with vegetarian options and creative cocktails."
   ❌ WRONG: "**Contemporary** Latin" or "- Vegetarian options"

2. **amenities**: ARRAY of features/services, NO emojis, NO bullets, NO markdown
   ✅ CORRECT: ["outdoor seating", "bar service", "vegetarian options", "accepts reservations", "cocktails", "wine list", "romantic atmosphere"]
   ❌ WRONG: ["✅ outdoor", "- bar", "**cocktails**"]
   
   Extract from phrases like:
   - "creative use of local ingredients" → "local ingredients"
   - "exceptional service" → "exceptional service"  
   - "inviting casual atmosphere" → "casual atmosphere"
   - "suitable for special occasions" → "special occasions"
   - "vegetarian options" → "vegetarian options"
   - "wine pairing" → "wine pairing"
   - "cocktail menu" → "cocktails"

3. **signature_dishes**: PLAIN TEXT describing popular dishes, NO markdown
   ✅ CORRECT: "Ceviche de guanábana, pulpo y jaibas, arancinis, cas dessert"
   ❌ WRONG: "**Ceviche** de guanábana" or "- Pulpo"

4. **atmosphere**: PLAIN TEXT description, NO markdown
   ✅ CORRECT: "Inviting casual atmosphere perfect for dates and special occasions"
   ❌ WRONG: "**Inviting** atmosphere" or "- Perfect for dates"

5. **dietary_options**: ARRAY like ["vegetarian", "vegan", "gluten-free"]

6. **price_details**: OBJECT with price ranges in LOCAL CURRENCY (CRC for Costa Rica)
   Extract from menu prices in the context and create ranges:
   
   Example from context:
   "Appetizers: CRC 5,500 - CRC 8,000"
   "Mains: CRC 7,500 - CRC 15,500"  
   "Desserts: CRC 5,000"
   "Cocktails: CRC 5,600 - CRC 6,500"
   
   ✅ CORRECT: {{
     "appetizers_range": "CRC 5,500 - 8,000",
     "mains_range": "CRC 7,500 - 15,500",
     "desserts_range": "CRC 5,000",
     "drinks_range": "CRC 5,600 - 6,500"
   }}
   
   ❌ WRONG: {{"appetizers_range": "5500-8000"}} (missing currency)
   
   Find the MINIMUM and MAXIMUM prices for each category from the menu items listed.

7. **special_experiences**: PLAIN TEXT about Chef's Table, tasting menus, etc., NO markdown
   ✅ CORRECT: "Chef's Table available Thursday-Saturday, 7-course tasting menu for 88 USD per person with optional wine pairing"
   ❌ WRONG: "**Chef's Table**" or "- 7-course menu"

8. **contact_details**: OBJECT with phone, email, website (if available)
   Example: {{"phone": "+506 6143 6871", "website": "https://..."}}

ABSOLUTELY NO:
- Markdown symbols: ** # - * _
- Emojis: ✅ ❌ 💰 🎯 ⭐
- Bullet points in text fields
- Formatting codes
- Citations in parentheses

Return ONLY valid JSON. Use null for missing data.
"""

            elif content_type == 'restaurant' and page_type == 'general':
                def decimal_to_float(obj):
                    from decimal import Decimal
                    if isinstance(obj, dict):
                        return {k: decimal_to_float(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [decimal_to_float(item) for item in obj]
                    elif isinstance(obj, Decimal):
                        return float(obj)
                    return obj
                
                serializable_data = decimal_to_float(existing_data)
                
                extraction_prompt = f"""You are extracting restaurant LISTING/GUIDE information from web search results. This is a GENERAL page with MULTIPLE restaurants, not a specific restaurant.

EXISTING DATA (from HTML - mostly empty/null):
{json.dumps(serializable_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ALL available fields for a restaurant listing/guide page:

REQUIRED FIELDS:

1. **area_name**: STRING - Name of the dining area/district (e.g., "Downtown San José Dining")
2. **location**: STRING - City or region covered
3. **available_restaurants**: ARRAY of restaurant names mentioned
4. **cuisine_types**: ARRAY of cuisine categories available (e.g., ["Italian", "Seafood", "Costa Rican"])
5. **dining_categories**: ARRAY of dining types (e.g., ["fine dining", "casual", "cafes", "street food"])
6. **description**: STRING - About the dining scene in this area

Extract ALL restaurants mentioned. Return valid JSON with complete data."""

            elif content_type == 'transportation' and page_type == 'specific':
                extraction_prompt = f"""You are extracting transportation route information from web search results. Parse the markdown/text and extract ALL transportation options available.

EXISTING DATA (already extracted from HTML):
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

CRITICAL: This is a route comparison page with MULTIPLE transportation options. Extract ALL options as an array.

Extract the following structure:

{{
  "route_name": "Origin to Destination" (e.g., "San José to Manuel Antonio"),
  "departure_location": "San José",
  "arrival_location": "Manuel Antonio National Park",
  "distance_km": 98.8,
  "route_options": [
    {{
      "transport_type": "bus|shuttle|car|taxi|flight|ferry",
      "operator": "operator name",
      "duration_hours": 3.42,
      "price_min_usd": 12,
      "price_max_usd": 16,
      "frequency": "daily|hourly|multiple times daily",
      "departure_point": "Terminal TRACOPA",
      "arrival_point": "Savegre",
      "route_description": "Bus from Terminal TRACOPA to Savegre",
      "booking_required": true|false,
      "amenities": ["wifi", "air conditioning", "bathroom"]
    }},
    // ... more options
  ],
  "fastest_option": {{
    "transport_type": "flight",
    "duration_hours": 2.1,
    "price_usd": 117
  }},
  "cheapest_option": {{
    "transport_type": "bus",
    "duration_hours": 3.42,
    "price_usd": 12
  }},
  "recommended_option": {{
    "transport_type": "shuttle",
    "duration_hours": 3.5,
    "price_usd": 45,
    "reason": "Best balance of comfort and price"
  }},
  "travel_tips": [
    "Book bus tickets in advance during peak season",
    "Traffic heavy on weekends and holidays",
    "Consider leaving early morning to avoid traffic"
  ],
  "things_to_know": [
    "Toll road costs approximately $5 USD",
    "Direct buses run daily from Terminal TRACOPA",
    "Parking scams near park entrance - use restaurant parking"
  ],
  "best_time_to_travel": "Early morning (6-7 AM) to avoid traffic"
}}

FORMATTING RULES:

1. **route_options**: ARRAY with ALL transportation methods found (bus, shuttle, drive, fly, etc.)
   - Extract EVERY option mentioned in the context
   - Convert minutes to hours decimals (3h 25m = 3.42)
   - Extract price ranges (min and max)

2. **departure_location** & **arrival_location**: Clean city/location names

3. **distance_km**: Extract distance if mentioned

4. **fastest_option**: The option with shortest duration_hours

5. **cheapest_option**: The option with lowest price_usd

6. **recommended_option**: Best balance (usually shuttle/private transport)

7. **travel_tips**: ARRAY of practical tips from context
   - NO markdown, NO emojis, NO bullets
   ✅ CORRECT: ["Book tickets in advance", "Traffic heavy on weekends"]
   ❌ WRONG: ["- Book tickets", "**Traffic** heavy"]

8. **things_to_know**: ARRAY of important info (parking, tolls, scams)
   - Extract warnings and practical information
   - NO markdown formatting

9. **best_time_to_travel**: Simple text recommendation

CONVERSION:
- Minutes to hours: 3h 25m = 3.42 (3 + 25/60)
- JOD to USD: multiply by 1.41 (if applicable)
- CRC to USD: divide by 500 (if applicable)

ABSOLUTELY NO:
- Markdown symbols: ** # - * _
- Emojis: ✅ ❌ 💰 🎯
- Bullet points in text
- Citations [source.com]
- Currency symbols in text

Return ONLY valid JSON with ALL transportation options found.
"""

            elif content_type == 'transportation' and page_type == 'general':
                extraction_prompt = f"""You are extracting transportation ROUTE GUIDE information from web search results. This is a GENERAL GUIDE with MULTIPLE transportation options for a route.

EXISTING DATA (from HTML - mostly empty/null):
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ALL available fields for a transportation route guide:

REQUIRED FIELDS:

1. **origin**: STRING - Starting location
2. **destination**: STRING - End location  
3. **overview**: STRING - General overview of travel between these locations
4. **distance_km**: NUMBER - Distance in kilometers
5. **route_options**: ARRAY of transportation options with details:
   - transport_name, transport_type, description, price_usd, duration_hours, schedule, frequency, pickup_locations, dropoff_locations, amenities
6. **fastest_option**: OBJECT - {type, duration_hours, price_usd}
7. **cheapest_option**: OBJECT - {type, duration_hours, price_usd}
8. **recommended_option**: OBJECT - {type, reason}
9. **travel_tips**: ARRAY of practical travel tips
10. **things_to_know**: ARRAY of important information
11. **best_time_to_travel**: STRING - Best time recommendation

Extract ALL transportation options mentioned (bus, shuttle, car, taxi, flight, etc.). Return valid JSON."""

            elif content_type == 'local_tips':
                extraction_prompt = f"""You are extracting local travel tips and destination guide information from web search results. Parse the markdown/text and convert to CLEAN structured data.

EXISTING DATA (already extracted from HTML):
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract ONLY MISSING fields (fields that are null/empty in EXISTING DATA) from the web search context.

CRITICAL FORMATTING RULES:

1. **title**: Extract the MAIN TITLE mentioned in the context
   Look for phrases like: "titled *\"Best places to visit in Costa Rica\"*" or "article title" or "guide to..."
   ✅ CORRECT: "Best places to visit in Costa Rica"
   ❌ WRONG: "**Best places**" or "titled Best places" or "*Best places*"
   
   Clean ALL markdown: remove *, **, _, #, italics, bold, etc.
   This is the MOST IMPORTANT field - extract it accurately from phrases like:
   - "This specific article, titled *\"Best places...\"*" → "Best places..."
   - "The page titled \"Guide to...\"" → "Guide to..."
   - "article called Best destinations" → "Best destinations"

2. **description**: PLAIN TEXT, 1-3 sentences, NO markdown, NO ** or - or #
   ✅ CORRECT: "A curated guide to the top destinations in Costa Rica including national parks, beaches, and cultural sites."
   ❌ WRONG: "**Guide** to destinations" or "- National parks"

3. **category**: ONE of: safety|money|transportation|culture|weather|health|general
   Infer from context (travel guides usually = general)

4. **practical_advice**: PLAIN TEXT with practical tips, NO markdown, NO bullets
   ✅ CORRECT: "Visit during dry season (December-April) for best weather. Book accommodations in advance for popular destinations. Carry both cash and cards as some areas have limited ATM access."
   ❌ WRONG: "**Visit** during dry season" or "- Book accommodations" or "• Carry cash"

5. **location**: Clean location name (country, city, or region)
   ✅ CORRECT: "Costa Rica"
   ❌ WRONG: "**Costa Rica**"

6. **cost_estimate**: PLAIN TEXT with budget info, NO markdown
   ✅ CORRECT: "Budget travelers: 30-50 USD/day, Mid-range: 75-150 USD/day, Luxury: 200+ USD/day"
   ❌ WRONG: "**Budget**: $30-50" or "- Budget: 30-50"

7. **best_time**: PLAIN TEXT about when to visit, NO markdown
   ✅ CORRECT: "December to April (dry season) for best weather, May to November for fewer tourists and lower prices"
   ❌ WRONG: "**December-April**" or "- Dry season"

8. **things_to_avoid**: ARRAY of warnings/cautions, NO emojis, NO markdown
   ✅ CORRECT: ["driving at night in rural areas", "leaving valuables in cars", "swimming in unsafe areas"]
   ❌ WRONG: ["❌ driving at night", "- Don't leave valuables", "**Don't swim**"]

9. **local_customs**: ARRAY of cultural tips, NO emojis, NO markdown
   ✅ CORRECT: ["greet with buenos días", "tip 10% in restaurants", "dress modestly in churches", "ask permission before photos"]
   ❌ WRONG: ["✅ greet", "- Tip 10%", "**Dress modestly**"]

10. **emergency_contacts**: ARRAY of objects with type/number/service
    ✅ CORRECT: [
      {{"type": "phone", "number": "911", "service": "Emergency Services"}},
      {{"type": "phone", "number": "128", "service": "Red Cross"}},
      {{"type": "address", "location": "San José Hospital", "service": "Main Hospital"}}
    ]

11. **destinations_covered**: ARRAY of destination objects with structured info
    
    ⚠️ CRITICAL: Extract AT LEAST 8-12 destinations OR ALL destinations mentioned (whichever is more).
    DO NOT limit yourself to only "top" destinations - include ALL mentioned places.
    
    For travel guides like "Best places to visit in [Country]", extract EVERY place listed:
    - Main tourist cities (capitals, major hubs)
    - National parks and nature reserves  
    - Beach towns and coastal areas
    - Mountain/highland regions
    - Cultural/historical sites
    - Adventure destinations
    - Wildlife viewing areas
    
    ✅ CORRECT FORMAT: [
      {{
        "name": "La Fortuna",
        "highlights": ["Arenal volcano views", "natural hot springs", "waterfall hikes", "adventure activities"],
        "best_for": "adventure",
        "activities": ["ziplining", "horseback riding", "hot springs", "waterfall visits"]
      }},
      {{
        "name": "Manuel Antonio",
        "highlights": ["white sand beaches", "national park", "wildlife viewing", "hiking trails"],
        "best_for": "beach",
        "activities": ["beach activities", "wildlife watching", "hiking", "snorkeling"]
      }},
      {{
        "name": "Tortuguero",
        "highlights": ["sea turtle nesting", "canal waterways", "jungle tours", "Caribbean coast"],
        "best_for": "nature",
        "activities": ["turtle watching", "boat tours", "kayaking", "wildlife spotting"]
      }},
      {{
        "name": "Osa Peninsula",
        "highlights": ["pristine wilderness", "Corcovado National Park", "biodiversity hotspot", "remote beaches"],
        "best_for": "nature",
        "activities": ["wildlife watching", "hiking", "whale watching", "snorkeling"]
      }},
      {{
        "name": "Monteverde",
        "highlights": ["cloud forest", "bird watching", "hanging bridges", "quetzal sightings"],
        "best_for": "nature",
        "activities": ["bird watching", "canopy tours", "night walks", "cloud forest hikes"]
      }},
      {{
        "name": "Tamarindo",
        "highlights": ["surfing beaches", "nightlife", "beach town vibe", "sunset views"],
        "best_for": "beach",
        "activities": ["surfing", "sunbathing", "dining", "nightlife"]
      }},
      {{
        "name": "Puerto Viejo",
        "highlights": ["Caribbean culture", "Afro-Caribbean heritage", "laid-back atmosphere", "beautiful beaches"],
        "best_for": "culture",
        "activities": ["beach activities", "cultural experiences", "snorkeling", "reggae music"]
      }},
      {{
        "name": "San José",
        "highlights": ["capital city", "museums", "urban culture", "transportation hub"],
        "best_for": "city",
        "activities": ["museum visits", "shopping", "dining", "city tours"]
      }}
      // Continue extracting ALL other destinations mentioned...
    ]
    
    REQUIREMENTS for EACH destination:
    - name: Clean destination name (city, park, region, or area)
    - highlights: 3-5 specific attractions/features that make it unique
    - best_for: ONE category - adventure|nature|beach|culture|city|wildlife
    - activities: 3-5 specific activities visitors can do there
    
    ⚠️ DO NOT skip destinations just because they seem "less important"
    ⚠️ DO NOT consolidate multiple places into one entry
    ⚠️ Extract individual cities/parks/regions separately

12. **budget_guide**: OBJECT with daily cost ranges
    ✅ CORRECT: {{
      "budget": "30-50 USD/day",
      "mid_range": "75-150 USD/day",
      "luxury": "200+ USD/day",
      "notes": "Costs include accommodation, meals, and activities"
    }}
    Extract if mentioned in context, otherwise null

13. **visa_info**: STRING with visa requirements
    ✅ CORRECT: "Free 90-day tourist visa on arrival for most countries. Check requirements for your nationality."
    Extract if mentioned, otherwise null

14. **recommended_duration**: STRING with suggested trip length
    ✅ CORRECT: "7-14 days to see main highlights, 2-3 weeks for comprehensive tour"
    Extract if mentioned, otherwise null

15. **language**: STRING with language info
    ✅ CORRECT: "Spanish (official), English widely spoken in tourist areas"
    Extract if mentioned, otherwise null

16. **currency**: STRING with currency info  
    ✅ CORRECT: "Costa Rican Colón (CRC), US Dollar widely accepted"
    Extract if mentioned, otherwise null

17. **safety_rating**: STRING with safety assessment
    ✅ CORRECT: "Generally safe for tourists, exercise normal precautions"
    Extract if mentioned, otherwise null

18. **transportation_tips**: STRING with getting around advice
    ✅ CORRECT: "Rental car recommended for flexibility. Public buses available but infrequent. Domestic flights connect major destinations. Shuttle services popular for tourist routes."
    Extract if mentioned, otherwise null

ABSOLUTELY NO:
- Markdown symbols: ** # - * _ ` []()
- Emojis: ✅ ❌ 💰 🎯 ⭐ 🌍
- Bullet points in text fields (convert to sentences)
- Citations like [source.com] or (source)
- Formatting codes
- HTML tags

CONVERSIONS:
- Bullet lists → Plain sentences or arrays
- Markdown bold/italic → Plain text
- Multiple paragraphs → Single paragraph separated by periods

PRIORITY EXTRACTION:
1. **title** - MOST IMPORTANT - extract from "titled", "called", "article name" phrases
2. **destinations_covered** - Structure all destinations mentioned
3. **practical_advice**, **best_time**, **cost_estimate** - Key travel planning info
4. All other fields

Return ONLY valid JSON. Use null for fields not found with high confidence.
"""

            else:
                extraction_prompt = f"""Extract structured information from this web search context.

EXISTING DATA:
{json.dumps(existing_data, indent=2, ensure_ascii=False)}

WEB SEARCH CONTEXT:
{web_search_context}

Extract any missing fields that you can find with high confidence.
Return valid JSON."""
            
            # Use GPT-4o-mini for extraction (cheap and fast)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction expert. Extract structured information from unstructured text and return valid JSON. Only extract fields with HIGH confidence."
                    },
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            extracted = json.loads(response.choices[0].message.content)
            
            # Count how many fields were extracted
            non_null_fields = {k: v for k, v in extracted.items() if v is not None and v != "" and v != []}
            
            logger.info(f"✅ [CONTEXT_EXTRACT] Extracted {len(non_null_fields)} fields from web context: {list(non_null_fields.keys())}")
            
            return extracted
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_EXTRACT] Error extracting from web context: {e}")
            import traceback
            traceback.print_exc()
            return {}


# Singleton instance
_web_search_service = None

def get_web_search_service() -> WebSearchService:
    """Get or create the web search service singleton."""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
