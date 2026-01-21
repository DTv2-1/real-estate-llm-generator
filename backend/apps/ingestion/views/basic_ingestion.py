"""
Basic URL and text ingestion views.
Handles single URL/text processing and property saving.
"""

import logging
import uuid
import threading
import time
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.tenants.models import Tenant
from apps.properties.models import Property, PropertyImage
from apps.properties.models_content import (
    RealEstateGeneral,
    RealEstateSpecific,
    RestaurantGeneral,
    RestaurantSpecific,
    TourGeneral,
    TourSpecific,
    TransportationGeneral,
    TransportationSpecific,
    LocalTipsGeneral,
    LocalTipsSpecific,
)
from apps.properties.serializers import PropertyDetailSerializer

from core.scraping.scraper import scrape_url, ScraperError
from core.llm.extraction import extract_content_data, ExtractionError, detect_content_type
from core.utils.website_detector import detect_source_website

from ..progress import ProgressTracker
from .base import serialize_for_json

logger = logging.getLogger(__name__)


# =============================================================================
# MODEL ROUTING HELPER
# =============================================================================

def get_model_for_content(content_type: str, page_type: str):
    """
    Determine which model to use based on content_type and page_type.
    
    Args:
        content_type: 'real_estate', 'restaurant', 'tour', 'transportation', 'local_tips'
        page_type: 'specific' (individual item) or 'general' (guide/listing page)
    
    Returns:
        Django model class
    """
    model_map = {
        ('real_estate', 'general'): RealEstateGeneral,
        ('real_estate', 'specific'): RealEstateSpecific,
        ('restaurant', 'general'): RestaurantGeneral,
        ('restaurant', 'specific'): RestaurantSpecific,
        ('tour', 'general'): TourGeneral,
        ('tour', 'specific'): TourSpecific,
        ('transportation', 'general'): TransportationGeneral,
        ('transportation', 'specific'): TransportationSpecific,
        ('local_tips', 'general'): LocalTipsGeneral,
        ('local_tips', 'specific'): LocalTipsSpecific,
    }
    
    key = (content_type, page_type)
    model = model_map.get(key)
    
    if not model:
        # Fallback to old Property model for backward compatibility
        logger.warning(f"⚠️ No specific model for content_type={content_type}, page_type={page_type}. Using Property model.")
        return Property
    
    logger.info(f"✅ Using model: {model.__name__} for content_type={content_type}, page_type={page_type}")
    return model


def prepare_data_for_model(extracted_data: dict, model_class):
    """
    Prepare extracted data for the specific model by:
    1. Mapping field names to model field names
    2. Moving content-specific fields to field_confidence if not in model
    3. Handling special field conversions
    
    Args:
        extracted_data: Raw extracted data dictionary
        model_class: Target Django model class
    
    Returns:
        Tuple of (prepared_data, extra_data_for_field_confidence)
    """
    # Get model field names
    model_fields = {f.name for f in model_class._meta.get_fields()}
    
    prepared_data = {}
    extra_data = {}
    
    # Special field mappings for different content types
    # Note: Some fields map to BOTH title AND their specific field
    field_mappings = {
        'property_name': 'title',  # Old property_name → new title field
        'restaurant_name': 'title',
        'tour_name': 'title',
        'route_name': 'title',  # Also keep route_name as separate field
        'tip_title': 'title',
    }
    
    for key, value in extracted_data.items():
        # Apply field mapping if exists
        target_field = field_mappings.get(key, key)
        
        # If field exists in model, use it directly
        if target_field in model_fields:
            prepared_data[target_field] = value
        
        # SPECIAL CASE: For transportation, keep both route_name AND title
        # Also keep departure_location, arrival_location as direct fields
        if key in ['route_name', 'departure_location', 'arrival_location'] and key in model_fields:
            prepared_data[key] = value
        elif target_field not in model_fields:
            # Store in extra_data for field_confidence
            extra_data[key] = value
    
    # Merge extra_data into field_confidence
    if extra_data:
        existing_fc = prepared_data.get('field_confidence', {})
        if isinstance(existing_fc, dict):
            existing_fc.update(extra_data)
            prepared_data['field_confidence'] = existing_fc
        else:
            prepared_data['field_confidence'] = extra_data
    
    logger.info(f"📦 Prepared data: {len(prepared_data)} direct fields, {len(extra_data)} in field_confidence")
    
    return prepared_data, extra_data


class IngestURLView(APIView):
    """
    Endpoint to ingest property from URL.
    
    POST /ingest/url
    {
        "url": "https://encuentra24.com/property/123",
        "use_websocket": true  // Optional: enables real-time progress updates
    }
    """
    
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]
    
    def _process_url_with_progress(self, url: str, source_website_override: str, user_content_type: str, task_id: str):
        """Process URL in background thread with progress updates."""
        import time
        tracker = ProgressTracker(task_id)
        
        try:
            # Small delay to allow frontend WebSocket to connect
            time.sleep(0.5)
            
            # Step 1: Scraping (0-30%)
            tracker.update(5, "Iniciando scraping...", stage="Scraping", substage="Conectando al sitio web")
            logger.info(f"Step 1: Scraping URL: {url}")
            
            scraped_data = scrape_url(url)
            tracker.update(20, "Contenido descargado", stage="Scraping", substage="Procesando HTML")
            
            if not scraped_data.get('success'):
                tracker.error("Failed to scrape URL")
                return
            
            html_content = scraped_data.get('html', scraped_data.get('text', ''))
            tracker.update(30, f"HTML extraído ({len(html_content)} caracteres)", stage="Scraping", substage="Completado")
            time.sleep(0.3)  # Allow UI to show stage
            
            # Step 2: Detection (30-40%)
            tracker.update(35, "Detectando sitio web y tipo de contenido...", stage="Análisis", substage="Identificando fuente")
            time.sleep(0.2)
            
            if source_website_override:
                source_website = source_website_override
            else:
                source_website = detect_source_website(url)
            
            # NEW: Detect content type (real_estate, tour, restaurant, etc.)
            # Strategy: Try fast methods first (domain/keywords), use LLM if confidence is low
            content_detection = detect_content_type(
                url=url,
                html=html_content,
                user_override=user_content_type,
                use_llm_fallback=False  # Try fast methods first
            )
            detected_content_type = content_detection['content_type']
            content_type_confidence = content_detection['confidence']
            detection_method = content_detection['method']
            
            # If confidence is low (<70%) and user didn't specify, use LLM for better accuracy
            if content_type_confidence < 0.70 and not user_content_type:
                logger.info(f"⚠️ Low confidence ({content_type_confidence:.0%}), retrying with LLM...")
                tracker.update(36, "Analizando con IA para mayor precisión...", stage="Análisis", substage="Clasificación avanzada")
                
                content_detection = detect_content_type(
                    url=url,
                    html=html_content,
                    user_override=user_content_type,
                    use_llm_fallback=True  # Use LLM for better accuracy
                )
                detected_content_type = content_detection['content_type']
                content_type_confidence = content_detection['confidence']
                detection_method = content_detection['method']
            
            logger.info(f"✅ Content type: {detected_content_type} (confidence: {content_type_confidence:.2%}, method: {detection_method})")
            
            tracker.update(37, f"Sitio: {source_website} | Tipo: {detected_content_type}", stage="Análisis")
            time.sleep(0.2)
            
            # NEW: Detect page type (specific item vs general guide/listing)
            from core.llm.extraction import detect_page_type
            
            page_detection = detect_page_type(
                url=url,
                html_content=html_content,
                content_type=detected_content_type
            )
            detected_page_type = page_detection['page_type']
            page_type_confidence = page_detection['confidence']
            page_detection_method = page_detection['method']
            
            logger.info(f"Page type detected: {detected_page_type} (confidence: {page_type_confidence:.2%}, method: {page_detection_method})")
            
            tracker.update(40, f"Sitio: {source_website} | Tipo: {detected_content_type} | Página: {detected_page_type}", stage="Análisis")
            time.sleep(0.2)
            
            # Step 3: Extraction (40-80%)
            tracker.update(50, "Usando extracción con IA...", stage="Extracción", substage="Procesando con LLM")
            # Use content-type specific extraction with page type detection
            extracted_data = extract_content_data(
                html_content, 
                content_type=detected_content_type, 
                page_type=detected_page_type,
                url=url
            )
            tracker.update(75, "IA completó la extracción", stage="Extracción", substage="Completado")
            extraction_method = 'llm_based'
            extractor_name = 'LLM-based'
            extraction_confidence = extracted_data.get('extraction_confidence', 0.5)
            
            # Step 4: Finalization (80-100%)
            time.sleep(0.2)
            tracker.update(85, "Finalizando...", stage="Procesamiento", substage="Limpiando datos")
            time.sleep(0.3)
            
            extracted_data['source_website'] = source_website
            tenant = Tenant.objects.first()
            extracted_data['tenant'] = tenant
            
            if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
                extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # Clean metadata fields
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning', 'extracted_at', 'field_confidence']
            for field in metadata_fields:
                extracted_data.pop(field, None)
            
            # Remove evidence fields
            evidence_fields = [key for key in list(extracted_data.keys()) if key.endswith('_evidence')]
            for field in evidence_fields:
                extracted_data.pop(field, None)
            
            # IMPORTANT: For general pages, preserve guide-specific fields
            # These fields are NOT in Property model but needed for frontend display
            guide_fields_to_preserve = [
                'destination', 'overview', 'tour_types_available',
                'price_range', 'best_season', 'best_time_of_day', 'duration_range',
                'tips', 'things_to_bring', 'featured_tours', 'total_tours_mentioned',
                'booking_tips', 'cuisine_types', 'property_types', 'featured_items_count'
            ]
            # Store them temporarily BEFORE removing anything
            preserved_data = {}
            if detected_page_type == 'general':
                logger.info(f"🔍 Preserving guide fields for general page...")
                for field in guide_fields_to_preserve:
                    if field in extracted_data:
                        preserved_data[field] = extracted_data[field]
                        logger.info(f"  ✅ Preserved: {field} = {extracted_data[field]}")
                logger.info(f"📦 Total preserved fields: {len(preserved_data)}")
            
            tenant = Tenant.objects.first()
            extracted_data['tenant'] = tenant
            
            # NEW: Post-process web_search_context to fill missing fields
            # IMPORTANT: Do this BEFORE removing tenant from extracted_data
            if extracted_data.get('web_search_context'):
                logger.info(f"🔍 [POST-PROCESS] Web search context available, extracting structured data...")
                tracker.update(78, "Procesando contexto web...", stage="Extracción", substage="Enriquecimiento")
                
                from core.llm.extraction import WebSearchService
                web_search = WebSearchService()
                
                # Create a clean copy for JSON serialization (remove tenant object)
                clean_data = {k: v for k, v in extracted_data.items() if k != 'tenant'}
                
                # Extract structured data from web context
                # CRITICAL: Pass page_type to extract correct schema (general vs specific)
                context_extracted = web_search.extract_from_web_context(
                    web_search_context=extracted_data['web_search_context'],
                    existing_data=clean_data,
                    content_type=detected_content_type,
                    page_type=detected_page_type
                )
                
                # Clean the web_search_context itself (remove markdown symbols)
                raw_context = extracted_data['web_search_context']
                import re
                # Remove markdown formatting
                cleaned_context = re.sub(r'\*\*', '', raw_context)  # Remove **
                cleaned_context = re.sub(r'^#{1,6}\s+', '', cleaned_context, flags=re.MULTILINE)  # Remove headers
                cleaned_context = re.sub(r'^\s*[-*+]\s+', '• ', cleaned_context, flags=re.MULTILINE)  # Replace bullets
                cleaned_context = re.sub(r'[✅❌💰🎯📍⭐🌍🎪🔗]', '', cleaned_context)  # Remove emojis
                extracted_data['web_search_context'] = cleaned_context.strip()
                
                # Merge: only add fields that are missing (null/empty) in original extraction
                fields_added = 0
                for key, value in context_extracted.items():
                    if value is not None and value != "" and value != []:
                        # Only add if field doesn't exist or is empty
                        current_value = extracted_data.get(key)
                        if current_value is None or current_value == "" or current_value == []:
                            extracted_data[key] = value
                            fields_added += 1
                            logger.info(f"  ✅ Added from context: {key} = {value}")
                
                logger.info(f"✅ [POST-PROCESS] Added {fields_added} fields from web search context")
                tracker.update(80, f"Añadidos {fields_added} campos desde contexto web", stage="Extracción", substage="Completado")
            
            tenant_id = extracted_data['tenant'].id if extracted_data.get('tenant') else None
            extracted_data['tenant_id'] = tenant_id
            extracted_data.pop('tenant', None)
            
            # Restore preserved guide fields
            if preserved_data:
                logger.info(f"♻️  Restoring {len(preserved_data)} guide fields...")
                extracted_data.update(preserved_data)
                logger.info(f"📦 Final extracted_data keys after restore: {list(extracted_data.keys())}")
            
            tracker.update(95, "Datos listos", stage="Procesamiento", substage="Preparando respuesta")
            
            # Send completion with serialized data INCLUDING content_type and page_type info
            logger.info(f"📦 Sending response - Page type: {detected_page_type}, Keys: {list(extracted_data.keys())[:10]}")
            
            tracker.complete(serialize_for_json({
                'property': extracted_data,
                'extraction_method': extraction_method,
                'extraction_confidence': extraction_confidence,
                'extractor_used': extractor_name,
                'content_type': detected_content_type,
                'content_type_confidence': content_type_confidence,
                'content_type_detection_method': detection_method,
                'page_type': detected_page_type,
                'page_type_confidence': page_type_confidence,
                'page_type_detection_method': page_detection_method,
            }), message="Extracción completada exitosamente")
            
            tracker.update(100, "¡Completado!", stage="Completado")
            
        except Exception as e:
            logger.error(f"❌ Error in background processing: {e}", exc_info=True)
            tracker.error(f"Error: {str(e)}")
    
    def post(self, request):
        """Process URL and extract property data."""
        
        logger.info(f"=== IngestURLView POST request received ===")
        
        url = request.data.get('url')
        source_website_override = request.data.get('source_website')
        user_content_type = request.data.get('content_type')  # NEW: Accept content_type from frontend
        use_websocket = request.data.get('use_websocket', False)
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If WebSocket requested, start background processing and return task_id
        if use_websocket:
            task_id = str(uuid.uuid4())
            logger.info(f"🔌 WebSocket mode - Starting background task: {task_id}")
            
            # Start processing in background thread
            thread = threading.Thread(
                target=self._process_url_with_progress,
                args=(url, source_website_override, user_content_type, task_id)
            )
            thread.daemon = True
            thread.start()
            
            return Response({
                'status': 'processing',
                'task_id': task_id,
                'message': 'Processing started. Connect to WebSocket for progress updates.'
            }, status=status.HTTP_202_ACCEPTED)
        
        # Original synchronous processing (fallback)
        try:
            # Step 1: Scrape the URL
            logger.info(f"Step 1: Scraping URL: {url}")
            scraped_data = scrape_url(url)
            logger.info(f"Scraping result: success={scraped_data.get('success')}")
            
            if not scraped_data.get('success'):
                logger.error("Scraping failed")
                return Response(
                    {'error': 'Failed to scrape URL'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            html_content = scraped_data.get('html', scraped_data.get('text', ''))
            logger.info(f"Original HTML size: {len(html_content)} chars")
            
            # Step 2: Detect source website and content type
            if source_website_override:
                source_website = source_website_override
                logger.info(f"Step 2: Using user-selected source website: {source_website}")
            else:
                source_website = detect_source_website(url)
                logger.info(f"Step 2: Auto-detected source website: {source_website}")
            
            # NEW: Detect content type (real_estate, tour, restaurant, etc.)
            content_detection = detect_content_type(
                url=url,
                html=html_content,
                user_override=user_content_type,
                use_llm_fallback=False
            )
            detected_content_type = content_detection['content_type']
            content_type_confidence = content_detection['confidence']
            detection_method = content_detection['method']
            
            logger.info(f"Content type detected: {detected_content_type} (confidence: {content_type_confidence:.2%}, method: {detection_method})")
            
            # NEW: Detect page type (specific item vs general guide/listing)
            from core.llm.extraction import detect_page_type
            
            page_detection = detect_page_type(
                url=url,
                html_content=html_content,
                content_type=detected_content_type
            )
            detected_page_type = page_detection['page_type']
            page_type_confidence = page_detection['confidence']
            page_detection_method = page_detection['method']
            
            logger.info(f"Page type detected: {detected_page_type} (confidence: {page_type_confidence:.2%}, method: {page_detection_method})")
            
            # Step 3: Extract using LLM with appropriate content type and page type
            logger.info(f"Extracting {detected_content_type} data with LLM (page_type: {detected_page_type})...")
            extracted_data = extract_content_data(
                content=html_content,
                content_type=detected_content_type,
                page_type=detected_page_type,
                url=url
            )
            
            logger.info(f"Extraction complete. Confidence: {extracted_data.get('extraction_confidence')}")
            
            extraction_method = 'llm_based'
            extractor_name = 'LLM-based'
            extraction_confidence = extracted_data.get('extraction_confidence', 0.5)
            
            # Step 4: Add source website and tenant
            extracted_data['source_website'] = source_website
            
            tenant = Tenant.objects.first()
            logger.info(f"Using tenant: {tenant.name if tenant else 'None'}")
            extracted_data['tenant'] = tenant
            
            # Set default user_roles if not specified
            if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
                extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            logger.info(f"User roles: {extracted_data['user_roles']}")
            
            # Remove fields that are not in the Property model
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning', 'extracted_at', 'field_confidence']
            for field in metadata_fields:
                extracted_data.pop(field, None)
            
            # Also remove all *_evidence fields
            evidence_fields = [key for key in list(extracted_data.keys()) if key.endswith('_evidence')]
            for field in evidence_fields:
                extracted_data.pop(field, None)
            
            # IMPORTANT: For general pages, preserve guide-specific fields
            guide_fields_to_preserve = [
                'destination', 'overview', 'tour_types_available', 'types_evidence',
                'price_range', 'best_season', 'best_time_of_day', 'duration_range',
                'tips', 'things_to_bring', 'featured_tours', 'total_tours_mentioned',
                'booking_tips', 'cuisine_types', 'property_types', 'featured_items_count'
            ]
            preserved_data = {}
            if detected_page_type == 'general':
                for field in guide_fields_to_preserve:
                    if field in extracted_data:
                        preserved_data[field] = extracted_data[field]
            
            logger.info(f"Cleaned extracted_data keys: {list(extracted_data.keys())}")
            
            # DON'T create Property - just return the extracted data for preview
            # Property will be created via separate save endpoint when user clicks "Save"
            logger.info("✓ Extraction successful - returning data for preview")
            
            # Convert tenant object to ID for JSON serialization
            tenant_id = extracted_data['tenant'].id if extracted_data.get('tenant') else None
            extracted_data['tenant_id'] = tenant_id
            extracted_data.pop('tenant', None)  # Remove the non-serializable tenant object
            
            # Restore preserved guide fields
            if preserved_data:
                extracted_data.update(preserved_data)
                logger.info(f"Restored guide fields: {list(preserved_data.keys())}")
            
            # Return extracted data without saving to database
            response_data = {
                'status': 'success',
                'message': f'Property data extracted successfully using {extraction_method} (not saved yet)',
                'property': extracted_data,
                'extraction_method': extraction_method,
                'extraction_confidence': extraction_confidence,
                'extractor_used': extractor_name,
                # NEW: Content type information
                'content_type': detected_content_type,
                'content_type_confidence': content_type_confidence,
                'content_type_detection_method': detection_method,
                # NEW: Page type information
                'page_type': detected_page_type,
                'page_type_confidence': page_type_confidence,
                'page_type_detection_method': page_detection_method,
            }
            
            logger.info(f"=== Request completed successfully ===")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ScraperError as e:
            logger.error(f"❌ Scraping error: {e}", exc_info=True)
            return Response(
                {'error': f'Scraping failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except ExtractionError as e:
            logger.error(f"❌ Extraction error: {e}", exc_info=True)
            return Response(
                {'error': f'Extraction failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"❌ Unexpected error in IngestURLView: {e}", exc_info=True)
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class IngestTextView(APIView):
    """
    Endpoint to ingest property from text.
    
    POST /ingest/text
    {
        "text": "Beautiful 3-bedroom villa in Tamarindo..."
    }
    """
    
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Process text and extract property data."""
        
        text = request.data.get('text')
        source_website_override = request.data.get('source_website')  # Optional: user-selected website
        
        if not text:
            return Response(
                {'error': 'Text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Extract property data with LLM
            logger.info("Extracting property data from text...")
            extracted_data = extract_content_data(
                content=text,
                content_type='real_estate',
                page_type='specific'
            )
            
            # Set source_website from user selection or default to 'other'
            extracted_data['source_website'] = source_website_override if source_website_override else 'other'
            logger.info(f"Using source_website: {extracted_data['source_website']}")
            
            # Add tenant
            tenant = Tenant.objects.first()
            extracted_data['tenant_id'] = tenant.id if tenant else None
            
            # Set default user_roles
            if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
                extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # DON'T create Property - just return extracted data for preview
            logger.info("✓ Extraction successful from text - returning data for preview")
            
            return Response({
                'status': 'success',
                'message': 'Property data extracted successfully (not saved yet)',
                'property': extracted_data,
                'extraction_confidence': extracted_data.get('extraction_confidence', 0),
                'field_confidence': extracted_data.get('field_confidence', {}),
            }, status=status.HTTP_200_OK)
            
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            return Response(
                {'error': f'Extraction failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class SavePropertyView(APIView):
    """
    Endpoint to save extracted property data to database.
    
    POST /ingest/save
    {
        "property_data": { ... extracted property fields ... }
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Save property data to database."""
        
        logger.info("=== SavePropertyView POST request received ===")
        
        property_data = request.data.get('property_data')
        
        if not property_data:
            return Response(
                {'error': 'property_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convert tenant_id back to tenant object
            tenant_id = property_data.get('tenant_id')
            if tenant_id:
                property_data['tenant'] = Tenant.objects.get(id=tenant_id)
                property_data.pop('tenant_id', None)
            elif 'tenant' not in property_data or not property_data['tenant']:
                property_data['tenant'] = Tenant.objects.first()
            
            # Set default user_roles
            if 'user_roles' not in property_data or not property_data['user_roles']:
                property_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # Remove fields that shouldn't be saved
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning']
            for field in metadata_fields:
                property_data.pop(field, None)
            
            # Remove all *_evidence fields
            evidence_fields = [key for key in list(property_data.keys()) if key.endswith('_evidence')]
            for field in evidence_fields:
                property_data.pop(field, None)
            
            # Map extractor field names to Property model field names
            field_mapping = {
                'title': 'property_name',
                'area_m2': 'square_meters',
                'listing_type': 'status',  # for_sale -> available
            }
            
            for old_name, new_name in field_mapping.items():
                if old_name in property_data:
                    property_data[new_name] = property_data.pop(old_name)
            
            # Convert listing_type values to status values
            if 'status' in property_data:
                status_mapping = {
                    'for_sale': 'available',
                    'for_rent': 'available',
                    'sold': 'sold',
                }
                property_data['status'] = status_mapping.get(property_data['status'], 'available')
            
            # Ensure property_type has a default value if missing or None
            # For non-real-estate content, use 'other' or first item from array
            if not property_data.get('property_type'):
                property_data['property_type'] = 'house'  # Default to 'house' if not specified
                logger.info(f"⚠️ property_type was missing/null, defaulting to 'house'")
            elif isinstance(property_data.get('property_type'), list):
                # If property_type is an array (e.g., cuisine types for restaurants), take first item
                # and store full array in field_confidence
                cuisine_array = property_data['property_type']
                property_data['property_type'] = 'commercial'  # Use 'commercial' for restaurants/businesses
                logger.info(f"⚠️ property_type was an array {cuisine_array}, using 'commercial' and storing array in field_confidence")
            elif len(str(property_data.get('property_type', ''))) > 20:
                # If property_type is too long, truncate or use default
                original = property_data['property_type']
                property_data['property_type'] = 'commercial'
                logger.info(f"⚠️ property_type was too long ({len(str(original))} chars), using 'commercial'")
            
            # Build location from address/city/province if location is empty
            if not property_data.get('location') and (property_data.get('city') or property_data.get('address')):
                location_parts = []
                if property_data.get('address'):
                    location_parts.append(property_data['address'])
                if property_data.get('city'):
                    location_parts.append(property_data['city'])
                if property_data.get('province'):
                    location_parts.append(property_data['province'])
                property_data['location'] = ', '.join(location_parts)
            
            # If location is still empty, use coordinates or default
            if not property_data.get('location'):
                if property_data.get('latitude') and property_data.get('longitude'):
                    property_data['location'] = f"{property_data['latitude']}, {property_data['longitude']}"
                    logger.info(f"⚠️ location was missing, using coordinates: {property_data['location']}")
                else:
                    property_data['location'] = 'Unknown Location'
                    logger.info(f"⚠️ location was missing, defaulting to 'Unknown Location'")
            
            # Remove fields that don't exist in Property model
            fields_to_remove = ['address', 'city', 'province', 'country', 'agent_name', 'agent_phone', 'agent_email']
            for field in fields_to_remove:
                property_data.pop(field, None)
            
            # Store content-type specific fields in field_confidence JSON
            # These fields are specific to restaurants, tours, etc. and don't have dedicated columns
            content_specific_fields = [
                'restaurant_name', 'cuisine_type', 'price_range', 'rating', 'number_of_reviews',
                'contact_phone', 'opening_hours', 'signature_dishes', 'atmosphere', 
                'dietary_options', 'special_experiences', 'contact_details',
                'web_search_context', 'web_search_sources', 'web_search_citations',
                'content_type_confidence', 'timestamp',
                # Tour-specific
                'tour_name', 'duration', 'difficulty', 'group_size', 'included_items',
                'excluded_items', 'meeting_point', 'cancellation_policy',
                # Transportation-specific
                'route_name', 'departure_location', 'arrival_location', 'travel_time',
                'transport_type', 'frequency', 'operator',
            ]
            
            # Extract content-specific data before removing
            extra_data = {}
            for field in content_specific_fields:
                if field in property_data:
                    extra_data[field] = property_data.pop(field)
            
            # Store extra data in field_confidence JSON field
            if extra_data:
                existing_field_confidence = property_data.get('field_confidence', {})
                if isinstance(existing_field_confidence, dict):
                    existing_field_confidence.update(extra_data)
                    property_data['field_confidence'] = existing_field_confidence
                else:
                    property_data['field_confidence'] = extra_data
                logger.info(f"📦 Stored {len(extra_data)} content-specific fields in field_confidence")
            
            # Determine model to use BEFORE checking duplicates
            content_type = property_data.get('content_type', 'real_estate')
            page_type = property_data.get('page_type', 'specific')
            model_class = get_model_for_content(content_type, page_type)
            
            # Check for duplicate by source_url using the correct model
            source_url = property_data.get('source_url')
            logger.info(f"🔍 Checking for duplicate in {model_class.__name__} - source_url: {source_url}")
            
            if source_url:
                existing = model_class.objects.filter(
                    source_url=source_url,
                    tenant=property_data.get('tenant')
                ).first()
                
                if existing:
                    logger.warning(f"⚠️ DUPLICATE DETECTED - {model_class.__name__} already exists:")
                    logger.warning(f"   - URL: {source_url}")
                    logger.warning(f"   - Existing ID: {existing.id}")
                    logger.warning(f"   - Existing Title: {existing.title}")
                    return Response({
                        'status': 'error',
                        'message': f'This {content_type} already exists in the database (ID: {existing.id})',
                        'property_id': str(existing.id),
                        'title': existing.title,
                        'duplicate': True
                    }, status=status.HTTP_409_CONFLICT)
                else:
                    logger.info(f"✅ No duplicate found in {model_class.__name__} - OK to save")
            
            # Separate ManyToMany fields (must be set after object creation)
            images_data = property_data.pop('images', [])
            amenities_data = property_data.pop('amenities', [])
            
            # Determine which model to use based on content_type and page_type
            content_type = property_data.get('content_type', 'real_estate')
            page_type = property_data.get('page_type', 'specific')
            
            logger.info(f"🔍 Detected content_type={content_type}, page_type={page_type}")
            
            model_class = get_model_for_content(content_type, page_type)
            
            # Prepare data for the specific model
            prepared_data, extra_data = prepare_data_for_model(property_data, model_class)
            
            # CRITICAL FIX: Ensure title is set from route_name for transportation
            if not prepared_data.get('title') and prepared_data.get('route_name'):
                prepared_data['title'] = prepared_data['route_name']
                logger.info(f"📝 Set title from route_name: {prepared_data['title']}")
            
            # CRITICAL FIX: If title is still NULL, try to extract from description or web context
            if not prepared_data.get('title'):
                # Try description first (truncate to reasonable length)
                if prepared_data.get('description'):
                    prepared_data['title'] = prepared_data['description'][:200]
                    logger.info(f"📝 Set title from description: {prepared_data['title'][:50]}...")
                # Otherwise use source_url as last resort
                elif prepared_data.get('source_url'):
                    # Extract meaningful part from URL
                    url = prepared_data['source_url']
                    title_from_url = url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                    prepared_data['title'] = title_from_url[:200] or "Extracted Content"
                    logger.info(f"📝 Set title from URL: {prepared_data['title']}")
                else:
                    prepared_data['title'] = "Extracted Content"
                    logger.info(f"📝 Set default title: {prepared_data['title']}")
            
            # Create object using the appropriate model
            logger.info(f"Creating {model_class.__name__} object from extracted data...")
            content_obj = model_class.objects.create(**prepared_data)
            
            # For backward compatibility, also log as "property_obj"
            property_obj = content_obj
            
            # Create PropertyImage objects from URL list (only for old Property model for now)
            if images_data and model_class == Property:
                logger.info(f"Creating {len(images_data)} PropertyImage objects...")
                created_count = 0
                for idx, image_url in enumerate(images_data):
                    if isinstance(image_url, str):  # Only process if it's a URL string
                        PropertyImage.objects.create(
                            property=property_obj,
                            image_url=image_url,
                            order=created_count,
                            is_primary=(created_count == 0)  # First image is primary
                        )
                        created_count += 1
                logger.info(f"✓ Created {created_count} images")
            
            # Set amenities (ArrayField - can be set directly) - only if model has amenities field
            if amenities_data and hasattr(content_obj, 'amenities'):
                logger.info(f"Setting {len(amenities_data)} amenities...")
                content_obj.amenities = amenities_data
                content_obj.save(update_fields=['amenities'])
            
            # Log success with appropriate field name
            title_field = 'title'
            if hasattr(content_obj, 'restaurant_name'):
                title_field = 'restaurant_name'
            elif hasattr(content_obj, 'tour_name'):
                title_field = 'tour_name'
            elif hasattr(content_obj, 'route_name'):
                title_field = 'route_name'
            elif hasattr(content_obj, 'property_name'):
                title_field = 'property_name'
            
            obj_title = getattr(content_obj, title_field, content_obj.title)
            
            logger.info(f"✓ {model_class.__name__} saved successfully: {content_obj.id}")
            logger.info(f"  - Title: {obj_title}")
            if hasattr(content_obj, 'price_usd') and content_obj.price_usd:
                logger.info(f"  - Price: ${content_obj.price_usd}")
            
            # For backward compatibility, keep property_obj reference
            property_obj = content_obj
            
            # Generate embeddings in background thread (non-blocking)
            logger.info("🔮 Starting background embedding generation...")
            import threading
            
            def generate_embedding_background():
                """Generate embedding in background thread."""
                try:
                    from core.llm.embeddings import generate_property_embedding
                    embedding = generate_property_embedding(property_obj)
                    if embedding:
                        property_obj.embedding = embedding
                        property_obj.save(update_fields=['embedding'])
                        # Use title field (works for all content types)
                        obj_name = getattr(property_obj, 'title', None) or str(property_obj.id)
                        logger.info(f"✅ [BACKGROUND] Embedding generated: {obj_name}")
                    else:
                        logger.warning(f"⚠️ [BACKGROUND] Embedding generation failed: {property_obj.id}")
                except Exception as e:
                    logger.error(f"❌ [BACKGROUND] Error generating embedding: {e}", exc_info=True)
            
            thread = threading.Thread(target=generate_embedding_background, daemon=True)
            thread.start()
            logger.info("✅ Background embedding thread started")
            
            # Return serialized property immediately without waiting for embedding
            serializer = PropertyDetailSerializer(property_obj)
            
            return Response({
                'status': 'success',
                'message': 'Property saved successfully',
                'property_id': str(property_obj.id),
                'property': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ Error saving property: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to save property: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


