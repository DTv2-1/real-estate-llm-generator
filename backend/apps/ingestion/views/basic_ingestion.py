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
from apps.properties.serializers import PropertyDetailSerializer

from core.scraping.scraper import scrape_url, ScraperError
from core.scraping.extractors import get_extractor
from core.llm.extraction import extract_property_data, extract_content_data, ExtractionError
from core.llm.content_detection import detect_content_type
from core.utils.website_detector import detect_source_website

from ..progress import ProgressTracker
from .base import serialize_for_json

logger = logging.getLogger(__name__)


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
            from core.llm.page_type_detection import detect_page_type
            
            page_detection = detect_page_type(
                url=url,
                html=html_content,
                content_type=detected_content_type
            )
            detected_page_type = page_detection['page_type']
            page_type_confidence = page_detection['confidence']
            page_detection_method = page_detection['method']
            
            logger.info(f"Page type detected: {detected_page_type} (confidence: {page_type_confidence:.2%}, method: {page_detection_method})")
            
            tracker.update(40, f"Sitio: {source_website} | Tipo: {detected_content_type} | Página: {detected_page_type}", stage="Análisis")
            time.sleep(0.2)
            
            # Step 3: Extraction (40-80%)
            tracker.update(45, "Obteniendo extractor...", stage="Extracción", substage="Configurando herramientas")
            time.sleep(0.2)
            
            # Only use site-specific extractor for real_estate
            if detected_content_type == 'real_estate':
                extractor = get_extractor(url)
                extractor_name = extractor.__class__.__name__
                use_site_extractor = extractor_name != 'BaseExtractor'
            else:
                use_site_extractor = False
                extractor_name = 'LLM-based'
            
            if use_site_extractor:
                tracker.update(50, f"Usando extractor específico: {extractor.site_name}", stage="Extracción", substage="Extracción rápida")
                time.sleep(0.3)
                extracted_data = extractor.extract(html_content, url)
                tracker.update(75, "Datos extraídos con éxito", stage="Extracción", substage="Completado")
                time.sleep(0.3)
                extraction_method = 'site_specific'
                extraction_confidence = 0.95
            else:
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
            from core.llm.page_type_detection import detect_page_type
            
            page_detection = detect_page_type(
                url=url,
                html=html_content,
                content_type=detected_content_type
            )
            detected_page_type = page_detection['page_type']
            page_type_confidence = page_detection['confidence']
            page_detection_method = page_detection['method']
            
            logger.info(f"Page type detected: {detected_page_type} (confidence: {page_type_confidence:.2%}, method: {page_detection_method})")
            
            # Step 3: Get site-specific extractor (only for real_estate)
            if detected_content_type == 'real_estate':
                extractor = get_extractor(url)
                extractor_name = extractor.__class__.__name__
                logger.info(f"Step 3: Using extractor: {extractor_name} for {extractor.site_name}")
                use_site_extractor = extractor_name != 'BaseExtractor'
            else:
                use_site_extractor = False
                extractor_name = 'LLM-based'
                logger.info(f"Step 3: Content type is {detected_content_type}, using LLM extraction")
            
            if use_site_extractor:
                logger.info(f"✓ Using site-specific extractor for real_estate - no LLM needed")
                
                # Extract using site-specific rules (fast, free, precise)
                extractor = get_extractor(url)
                extracted_data = extractor.extract(html_content, url)
                logger.info(f"Extraction complete using {extractor_name}")
                logger.info(f"Extracted fields: {[k for k, v in extracted_data.items() if v is not None]}")
                
                extraction_method = 'site_specific'
                extraction_confidence = 0.95  # High confidence for rule-based extraction
                
            else:
                logger.info(f"⚠ Using LLM extraction for content type: {detected_content_type}, page type: {detected_page_type}")
                
                # Use LLM-based extraction with appropriate content type AND page type prompt
                logger.info(f"Extracting {detected_content_type} data with LLM (page_type: {detected_page_type})...")
                extracted_data = extract_content_data(
                    content=html_content,
                    content_type=detected_content_type,
                    page_type=detected_page_type,
                    url=url
                )
                
                logger.info(f"Extraction complete. Confidence: {extracted_data.get('extraction_confidence')}")
                
                extraction_method = 'llm_based'
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
            extracted_data = extract_property_data(text)
            
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
            if not property_data.get('property_type'):
                property_data['property_type'] = 'house'  # Default to 'house' if not specified
                logger.info(f"⚠️ property_type was missing/null, defaulting to 'house'")
            
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
            
            # Check for duplicate by source_url
            source_url = property_data.get('source_url')
            logger.info(f"🔍 Checking for duplicate - source_url: {source_url}")
            
            if source_url:
                existing = Property.objects.filter(
                    source_url=source_url,
                    tenant=property_data.get('tenant')
                ).first()
                
                if existing:
                    logger.warning(f"⚠️ DUPLICATE DETECTED - Property already exists:")
                    logger.warning(f"   - URL: {source_url}")
                    logger.warning(f"   - Existing ID: {existing.id}")
                    logger.warning(f"   - Existing Name: {existing.property_name}")
                    return Response({
                        'status': 'error',
                        'message': f'This property already exists in the database (ID: {existing.id})',
                        'property_id': str(existing.id),
                        'property_name': existing.property_name,
                        'duplicate': True
                    }, status=status.HTTP_409_CONFLICT)
                else:
                    logger.info(f"✅ No duplicate found - OK to save")
            
            # Separate ManyToMany fields (must be set after object creation)
            images_data = property_data.pop('images', [])
            amenities_data = property_data.pop('amenities', [])
            
            # Create Property
            logger.info("Creating Property object from saved data...")
            property_obj = Property.objects.create(**property_data)
            
            # Create PropertyImage objects from URL list
            if images_data:
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
            
            # Set amenities (ArrayField - can be set directly)
            if amenities_data:
                logger.info(f"Setting {len(amenities_data)} amenities...")
                property_obj.amenities = amenities_data
                property_obj.save(update_fields=['amenities'])
            
            logger.info(f"✓ Property saved successfully: {property_obj.id}")
            logger.info(f"  - Name: {property_obj.property_name}")
            logger.info(f"  - Price: ${property_obj.price_usd}")
            
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
                        logger.info(f"✅ [BACKGROUND] Embedding generated: {property_obj.property_name}")
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


