"""
Batch processing views for multiple URL ingestion.
Handles batch operations and exports to Google Sheets or database.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.tenants.models import Tenant
from apps.users.models import CustomUser
from apps.properties.models import Property

from core.scraping.scraper import scrape_url
from core.llm.extraction import extract_property_data

from ..google_sheets import GoogleSheetsService

logger = logging.getLogger(__name__)


class IngestBatchView(APIView):
    """
    Endpoint to ingest multiple properties at once.
    
    POST /ingest/batch
    {
        "urls": ["https://...", "https://..."],
        "async": true
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Process multiple URLs in batch."""
        
        urls = request.data.get('urls', [])
        run_async = request.data.get('async', False)
        results_sheet_id = request.data.get('results_sheet_id')
        
        if not urls or not isinstance(urls, list):
            return Response(
                {'error': 'URLs array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(urls) > 50:
            return Response(
                {'error': 'Maximum 50 URLs per batch'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if run_async:
            # Queue for async processing with Celery
            from apps.ingestion.tasks import ingest_url_task
            
            task_ids = []
            for url in urls:
                if request.user.is_authenticated:
                    tenant_id = str(request.user.tenant_id)
                    user_id = str(request.user.id)
                else:
                    tenant_id = str(Tenant.objects.first().id)
                    user_id = str(CustomUser.objects.first().id)

                task = ingest_url_task.delay(
                    url=url,
                    tenant_id=tenant_id,
                    user_id=user_id
                )
                task_ids.append(task.id)
            
            return Response({
                'status': 'queued',
                'message': f'{len(urls)} properties queued for processing',
                'task_ids': task_ids
            }, status=status.HTTP_202_ACCEPTED)
        
        else:
            # Process synchronously
            from apps.ingestion.google_sheets import GoogleSheetsService
            
            # Initialize Google Sheets service if results_sheet_id provided
            sheets_service = None
            if results_sheet_id:
                try:
                    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 
                                                  'credentials/google-sheets-credentials.json')
                    sheets_service = GoogleSheetsService(credentials_path)
                    logger.info(f"Google Sheets service initialized for results sheet: {results_sheet_id}")
                except Exception as e:
                    logger.error(f"Failed to initialize Google Sheets service: {e}")
            
            results = []
            for url in urls:
                try:
                    scraped_data = scrape_url(url)
                    extracted_data = extract_property_data(
                        scraped_data.get('html', ''), 
                        url=url
                    )
                    if request.user.is_authenticated:
                        extracted_data['tenant'] = request.user.tenant
                    else:
                        extracted_data['tenant'] = Tenant.objects.first()
                    extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
                    
                    property_obj = Property.objects.create(**extracted_data)
                    
                    result = {
                        'url': url,
                        'status': 'success',
                        'property_id': str(property_obj.id)
                    }
                    results.append(result)
                    
                    # Write to Google Sheets if service is available
                    if sheets_service and results_sheet_id:
                        try:
                            result_row_data = {
                                'url': url,
                                'property_data': {
                                    'title': extracted_data.get('title', ''),
                                    'price': extracted_data.get('price_usd'),
                                    'bedrooms': extracted_data.get('bedrooms'),
                                    'bathrooms': extracted_data.get('bathrooms'),
                                    'area': extracted_data.get('square_meters'),
                                    'location': extracted_data.get('location', ''),
                                    'property_type': extracted_data.get('property_type', ''),
                                },
                                'status': 'Procesado',
                                'notes': f"Property ID: {str(property_obj.id)}",
                                'property_id': str(property_obj.id)
                            }
                            sheets_service.append_result_row(results_sheet_id, result_row_data)
                        except Exception as e:
                            logger.error(f"Failed to write to Google Sheets: {e}")
                    
                except Exception as e:
                    result = {
                        'url': url,
                        'status': 'failed',
                        'error': str(e)
                    }
                    results.append(result)
                    
                    # Write error to Google Sheets if service is available
                    if sheets_service and results_sheet_id:
                        try:
                            error_row_data = {
                                'url': url,
                                'property_data': {},
                                'status': 'Error',
                                'notes': str(e),
                                'property_id': ''
                            }
                            sheets_service.append_result_row(results_sheet_id, error_row_data)
                        except Exception as sheet_error:
                            logger.error(f"Failed to write error to Google Sheets: {sheet_error}")
            
            response_data = {
                'status': 'completed',
                'results': results
            }
            
            if results_sheet_id:
                response_data['results_spreadsheet'] = {
                    'spreadsheet_id': results_sheet_id,
                    'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{results_sheet_id}/edit'
                }
            
            return Response(response_data, status=status.HTTP_200_OK)




class BatchExportToSheetsView(APIView):
    """
    Export batch results to Google Sheets with dynamic columns and automatic tabs.
    Creates separate tabs for specific vs general pages within the same spreadsheet.
    
    POST /ingest/batch-export/sheets/
    Body: {
        "sheet_id": "1abc...",
        "results": [...],
        "content_type": "tour" | "real_estate" | "restaurant" | etc
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def _get_sheet_name(self, page_type: str) -> str:
        """
        Get friendly sheet name for page type.
        """
        names = {
            'specific': 'Específicos',
            'general': 'Generales'
        }
        return names.get(page_type, page_type.capitalize())
    
    def _get_column_schema(self, content_type: str, page_type: str) -> dict:
        """
        Define column schemas for different content types and page types.
        Returns: {'headers': [...], 'field_keys': [...]}
        """
        
        # TOUR - SPECIFIC PAGE
        if content_type == 'tour' and page_type == 'specific':
            return {
                'headers': [
                    'Nombre del Tour', 'Tipo de Tour', 'Precio (USD)', 'Precio Adults', 'Precio Children',
                    'Precio Students', 'Precio Nationals', 'Precio Groups', 'Precio Range',
                    'Duración (horas)', 'Nivel de Dificultad', 'Ubicación', 'Descripción',
                    'Qué Incluye', 'Qué Excluye', 'Máx. Participantes', 'Idiomas Disponibles',
                    'Pickup Incluido', 'Edad Mínima', 'Política de Cancelación',
                    'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'tour_name', 'tour_type', 'price_usd', 'price_details.adults', 'price_details.children',
                    'price_details.students', 'price_details.nationals', 'price_details.groups', 'price_details.range',
                    'duration_hours', 'difficulty_level', 'location', 'description',
                    'included_items', 'excluded_items', 'max_participants', 'languages_available',
                    'pickup_included', 'minimum_age', 'cancellation_policy',
                    'extraction_confidence', 'source_url'
                ]
            }
        
        # TOUR - GENERAL PAGE (GUIDE)
        elif content_type == 'tour' and page_type == 'general':
            return {
                'headers': [
                    'Destino', 'Ubicación', 'Resumen General', 'Tipos de Tours Disponibles',
                    'Regiones', 'Precio Mín (USD)', 'Precio Máx (USD)', 'Precio Típico (USD)',
                    'Mejor Temporada', 'Mejor Hora del Día', 'Rango de Duración',
                    'Consejos', 'Qué Llevar', 'Tours Destacados', 'Total Tours Mencionados',
                    'Consejos de Reserva', 'Actividades por Temporada', 'FAQs',
                    'Apto para Familias', 'Info de Accesibilidad', 'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'destination', 'location', 'overview', 'tour_types_available',
                    'regions', 'price_range.min_usd', 'price_range.max_usd', 'price_range.typical_usd',
                    'best_season', 'best_time_of_day', 'duration_range',
                    'tips', 'things_to_bring', 'featured_tours', 'total_tours_mentioned',
                    'booking_tips', 'seasonal_activities', 'faqs',
                    'family_friendly', 'accessibility_info', 'extraction_confidence', 'source_url'
                ]
            }
        
        # REAL ESTATE - SPECIFIC PAGE
        elif content_type == 'real_estate' and page_type == 'specific':
            return {
                'headers': [
                    'Título', 'Precio (USD)', 'Ubicación', 'Ciudad', 'Provincia', 'País',
                    'Tipo de Propiedad', 'Tipo de Listado', 'Habitaciones', 'Baños',
                    'Área (m²)', 'Tamaño Lote (m²)', 'Espacios de Estacionamiento',
                    'Descripción', 'Amenidades', 'Fecha de Listado', 'Estado',
                    'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'title', 'price_usd', 'location', 'city', 'province', 'country',
                    'property_type', 'listing_type', 'bedrooms', 'bathrooms',
                    'area_m2', 'lot_size_m2', 'parking_spaces',
                    'description', 'amenities', 'date_listed', 'status',
                    'extraction_confidence', 'source_url'
                ]
            }
        
        # REAL ESTATE - GENERAL PAGE
        elif content_type == 'real_estate' and page_type == 'general':
            return {
                'headers': [
                    'Destino', 'Ubicación', 'Resumen General', 'Tipos de Propiedades',
                    'Precio Mín (USD)', 'Precio Máx (USD)', 'Propiedades Destacadas',
                    'Total Propiedades', 'Regiones', 'Consejos', 'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'destination', 'location', 'overview', 'property_types',
                    'price_range.min_usd', 'price_range.max_usd', 'featured_items',
                    'total_items_mentioned', 'regions', 'tips', 'extraction_confidence', 'source_url'
                ]
            }
        
        # RESTAURANT - SPECIFIC PAGE
        elif content_type == 'restaurant' and page_type == 'specific':
            return {
                'headers': [
                    'Nombre', 'Tipo de Cocina', 'Rango de Precio', 'Precio Promedio (USD)',
                    'Ubicación', 'Horario', 'Ambiente', 'Reservas Requeridas',
                    'Platillos Destacados', 'Opciones Dietéticas', 'Código de Vestimenta',
                    'Teléfono', 'Descripción', 'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'restaurant_name', 'cuisine_type', 'price_range', 'average_price_usd',
                    'location', 'hours', 'ambiance', 'reservations_required',
                    'signature_dishes', 'dietary_options', 'dress_code',
                    'phone', 'description', 'extraction_confidence', 'source_url'
                ]
            }
        
        # RESTAURANT - GENERAL PAGE
        elif content_type == 'restaurant' and page_type == 'general':
            return {
                'headers': [
                    'Destino', 'Ubicación', 'Resumen General', 'Tipos de Cocina',
                    'Precio Mín (USD)', 'Precio Máx (USD)', 'Restaurantes Destacados',
                    'Total Restaurantes', 'Consejos', 'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'destination', 'location', 'overview', 'cuisine_types',
                    'price_range.min_usd', 'price_range.max_usd', 'featured_items',
                    'total_items_mentioned', 'tips', 'extraction_confidence', 'source_url'
                ]
            }
        
        # TRANSPORTATION - SPECIFIC SERVICE
        elif content_type == 'transportation' and page_type == 'specific':
            return {
                'headers': [
                    'Nombre', 'Tipo', 'Ruta', 'Precio (USD)', 'Duración (horas)',
                    'Horario', 'Frecuencia', 'Punto de Recogida', 'Punto de Entrega',
                    'Reserva Requerida', 'Capacidad de Equipaje', 'Teléfono',
                    'Descripción', 'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'transport_name', 'transport_type', 'route', 'price_usd', 'duration_hours',
                    'schedule', 'frequency', 'pickup_location', 'dropoff_location',
                    'booking_required', 'luggage_allowance', 'contact_phone',
                    'description', 'extraction_confidence', 'source_url'
                ]
            }
        
        # TRANSPORTATION - GENERAL GUIDE
        elif content_type == 'transportation' and page_type == 'general':
            return {
                'headers': [
                    'Origen', 'Destino', 'Distancia (km)', 'Resumen General',
                    'Opciones Disponibles', 'Opción Más Rápida', 'Opción Más Económica',
                    'Opción Recomendada', 'Consejos de Viaje', 'Información Importante',
                    'Mejor Momento para Viajar', 'Confianza Extracción', 'URL'
                ],
                'field_keys': [
                    'origin', 'destination', 'distance_km', 'overview',
                    'route_options', 'fastest_option.transport_type', 'cheapest_option.transport_type',
                    'recommended_option.transport_type', 'travel_tips', 'things_to_know',
                    'best_time_to_travel', 'extraction_confidence', 'source_url'
                ]
            }
        
        # DEFAULT - Try to extract common fields
        else:
            return {
                'headers': ['Título', 'Ubicación', 'Precio (USD)', 'Descripción', 'URL'],
                'field_keys': ['title', 'location', 'price_usd', 'description', 'url']
            }
    
    def _extract_field_value(self, obj: dict, key_path: str) -> str:
        """
        Extract value from nested dict using dot notation (e.g., 'price_range.min_usd').
        Handles arrays, nested objects, and None values.
        """
        keys = key_path.split('.')
        value = obj
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return 'N/A'
        
        # Format value
        if value is None:
            return 'N/A'
        elif isinstance(value, list):
            if len(value) == 0:
                return 'N/A'
            # Format arrays nicely
            if all(isinstance(item, str) for item in value):
                return ', '.join(value)
            elif all(isinstance(item, dict) for item in value):
                # Special formatting for different types of objects
                formatted_items = []
                for item in value:
                    # FAQs: "Q: ... A: ..."
                    if 'question' in item and 'answer' in item:
                        formatted_items.append(f"Q: {item['question']} | A: {item['answer']}")
                    # Seasonal activities: "Season: ... Activities: ..."
                    elif 'season' in item and 'recommended_activities' in item:
                        activities = ', '.join(item.get('recommended_activities', []))
                        formatted_items.append(f"{item['season']}: {activities}")
                    # Featured tours/items with name
                    elif 'name' in item:
                        formatted_items.append(item['name'])
                    elif 'tour_name' in item:
                        formatted_items.append(item['tour_name'])
                    # Transportation route options
                    elif 'transport_type' in item:
                        parts = [item['transport_type']]
                        if item.get('price_usd'):
                            parts.append(f"${item['price_usd']}")
                        if item.get('duration_hours'):
                            parts.append(f"{item['duration_hours']}h")
                        formatted_items.append(' - '.join(parts))
                    # Price details
                    elif 'adults' in item or 'children' in item:
                        parts = []
                        if 'adults' in item:
                            parts.append(f"Adultos: ${item['adults']}")
                        if 'children' in item:
                            parts.append(f"Niños: ${item['children']}")
                        if 'students' in item:
                            parts.append(f"Estudiantes: ${item['students']}")
                        formatted_items.append(' | '.join(parts))
                    # Default: convert to string
                    else:
                        formatted_items.append(str(item))
                
                return ' || '.join(formatted_items)
            else:
                return ', '.join(str(v) for v in value)
        elif isinstance(value, bool):
            return 'Sí' if value else 'No'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    def post(self, request):
        sheet_id = request.data.get('sheet_id')
        results = request.data.get('results', [])
        content_type = request.data.get('content_type', 'real_estate')
        
        if not sheet_id:
            return Response({
                'error': 'sheet_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not results:
            return Response({
                'error': 'No results to export'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Initialize Google Sheets service
            sheets_service = GoogleSheetsService()
            
            # Group results by page_type (specific vs general)
            groups = {}
            for result in results:
                page_type = result.get('page_type', 'specific')
                if page_type not in groups:
                    groups[page_type] = []
                groups[page_type].append(result)
            
            logger.info(f"📊 Exporting {len(results)} items of type '{content_type}' grouped into {len(groups)} tabs")
            
            exported_tabs = []
            
            # Export each group to its own tab
            for page_type, group_results in groups.items():
                # Get sheet name for this page type
                sheet_name = self._get_sheet_name(page_type)
                
                logger.info(f"📝 Processing tab '{sheet_name}' with {len(group_results)} items...")
                
                # Get or create the sheet (tab)
                sheets_service.get_or_create_sheet(sheet_id, sheet_name)
                
                # Get column schema for this content type and page type
                schema = self._get_column_schema(content_type, page_type)
                headers = schema['headers']
                field_keys = schema['field_keys']
                
                logger.info(f"   Columns: {len(headers)} fields")
                
                # Clear the tab before writing
                sheets_service.clear_sheet(sheet_id, sheet_name)
                
                # Prepare header row + data rows
                rows = [headers]  # First row is headers
                
                for result in group_results:
                    row = []
                    for key in field_keys:
                        value = self._extract_field_value(result, key)
                        row.append(value)
                    rows.append(row)
                
                # Calculate range dynamically
                num_cols = len(headers)
                col_letter = chr(ord('A') + num_cols - 1) if num_cols <= 26 else 'Z'
                range_notation = f'{sheet_name}!A:{col_letter}'
                
                # Write to tab (headers + data)
                sheets_service.append_rows(sheet_id, range_notation, rows, sheet_name)
                
                exported_tabs.append({
                    'tab_name': sheet_name,
                    'page_type': page_type,
                    'items_count': len(group_results),
                    'columns_count': len(headers)
                })
                
                logger.info(f"✅ Exported {len(group_results)} items to tab '{sheet_name}'")
            
            logger.info(f"✅ All exports completed for {content_type}")
            
            return Response({
                'status': 'success',
                'exported_count': len(results),
                'sheet_id': sheet_id,
                'content_type': content_type,
                'tabs': exported_tabs
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error exporting to Google Sheets: {e}", exc_info=True)
            return Response({
                'error': str(e),
                'message': 'Failed to export to Google Sheets'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class BatchExportToDatabaseView(APIView):
    """
    Save batch results to database.
    
    POST /ingest/batch-export/database/
    Body: {
        "results": [...]
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        results = request.data.get('results', [])
        
        if not results:
            return Response({
                'error': 'No results to save'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create default tenant
            tenant, _ = Tenant.objects.get_or_create(
                slug='default',
                defaults={
                    'name': 'Default Tenant',
                    'domain': 'http://localhost:8000',
                    'is_active': True
                }
            )
            
            # Get or create default user
            user, _ = CustomUser.objects.get_or_create(
                email='admin@example.com',
                defaults={
                    'username': 'admin',
                    'tenant': tenant
                }
            )
            
            saved_count = 0
            errors = []
            
            for result in results:
                try:
                    # Check if property already exists by URL
                    url = result.get('url', '')
                    if url and Property.objects.filter(source_url=url, tenant=tenant).exists():
                        logger.info(f"⏭️  Property already exists: {url}")
                        continue
                    
                    # Create property with correct field names
                    property_data = {
                        'tenant': tenant,
                        'property_name': result.get('title', 'Untitled Property'),
                        'description': result.get('description', ''),
                        'price_usd': result.get('price_usd'),
                        'location': result.get('location', ''),
                        'property_type': result.get('property_type', 'land'),
                        'source_url': url,
                        'source_website': 'other',
                        'status': 'available',
                        'user_roles': ['buyer', 'staff', 'admin']
                    }
                    
                    # Add optional fields if present
                    if result.get('bedrooms'):
                        property_data['bedrooms'] = result.get('bedrooms')
                    if result.get('bathrooms'):
                        property_data['bathrooms'] = result.get('bathrooms')
                    if result.get('area_m2'):
                        property_data['square_meters'] = result.get('area_m2')
                    if result.get('lot_size_m2'):
                        property_data['lot_size_m2'] = result.get('lot_size_m2')
                    if result.get('amenities'):
                        property_data['amenities'] = result.get('amenities', [])
                    
                    property_obj = Property.objects.create(**property_data)
                    saved_count += 1
                    logger.info(f"✅ Saved property: {property_obj.property_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error saving property: {e}")
                    errors.append(str(e))
            
            return Response({
                'status': 'success',
                'saved_count': saved_count,
                'total_count': len(results),
                'errors': errors if errors else None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}", exc_info=True)
            return Response({
                'error': str(e),
                'message': 'Failed to save to database'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
