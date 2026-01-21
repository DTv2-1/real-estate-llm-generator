"""
Utility views for ingestion system.
Includes stats, supported websites, content types, embeddings, etc.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.llm.content_types import get_all_content_types
from core.llm.chatbot.embeddings import generate_property_embedding
from apps.properties.models import Property
from ..serializers import SupportedWebsiteSerializer
from ..google_sheets import GoogleSheetsService

logger = logging.getLogger(__name__)


class SupportedWebsitesView(APIView):
    """
    Endpoint to get list of supported websites with their configurations.
    
    GET /ingest/supported-websites/
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return list of supported websites."""
        
        # Define supported websites with their configurations
        # All websites now use LLM-based extraction (no site-specific extractors)
        websites = [
            {
                'id': 'brevitas',
                'name': 'Brevitas',
                'url': 'https://brevitas.com',
                'color': '#f59e0b',
                'active': True,
                'has_extractor': True  # LLM-based
            },
            {
                'id': 'encuentra24',
                'name': 'Encuentra24',
                'url': 'https://encuentra24.com/costa-rica-en',
                'color': '#10b981',
                'active': True,
                'has_extractor': True  # LLM-based
            },
            {
                'id': 'coldwellbanker',
                'name': 'Coldwell Banker',
                'url': 'https://www.coldwellbankercostarica.com',
                'color': '#8b5cf6',
                'active': True,
                'has_extractor': True  # LLM-based
            },
            {
                'id': 'other',
                'name': 'Other Sources',
                'url': None,
                'color': '#6b7280',
                'active': True,
                'has_extractor': True  # LLM-based
            }
        ]
        
        serializer = SupportedWebsiteSerializer(websites, many=True)
        
        return Response({
            'status': 'success',
            'websites': serializer.data,
            'extraction_method': 'llm_based',
            'note': 'All websites use intelligent LLM-based extraction'
        }, status=status.HTTP_200_OK)


class ContentTypesView(APIView):
    """
    Endpoint to get list of available content types for multi-domain extraction.
    
    GET /ingest/content-types/
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return list of available content types."""
        
        content_types = get_all_content_types()
        
        return Response({
            'status': 'success',
            'content_types': content_types,
            'total': len(content_types)
        }, status=status.HTTP_200_OK)


class IngestionStatsView(APIView):
    """
    Endpoint to get ingestion statistics.
    
    GET /ingest/stats/
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get ingestion statistics."""
        try:
            # Get timezone-aware dates
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = today_start.replace(day=1)
            
            # Count properties created today, this week, and this month
            properties_today = Property.objects.filter(created_at__gte=today_start).count()
            properties_this_week = Property.objects.filter(created_at__gte=week_start).count()
            properties_this_month = Property.objects.filter(created_at__gte=month_start).count()
            
            # Get last 10 properties
            recent_properties = Property.objects.order_by('-created_at')[:10]
            recent_properties_data = [
                {
                    'id': str(prop.id),
                    'title': prop.property_name or 'Sin título',
                    'location': prop.location or 'Ubicación no especificada',
                    'price_usd': float(prop.price_usd) if prop.price_usd else None,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
                    'source_website': prop.source_website or 'Desconocido',
                    'created_at': prop.created_at.isoformat()
                }
                for prop in recent_properties
            ]
            
            return Response({
                'status': 'success',
                'properties_today': properties_today,
                'properties_this_week': properties_this_week,
                'properties_this_month': properties_this_month,
                'recent_properties': recent_properties_data,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching ingestion stats: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateEmbeddingsView(APIView):
    """
    Admin endpoint to generate embeddings for all properties without embeddings.
    
    POST /ingest/generate-embeddings
    {
        "force": false  // Optional: regenerate even if embeddings exist
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]  # TODO: Add admin-only permission in production
    
    def post(self, request):
        """Generate embeddings for properties."""
        
        logger.info("=== GenerateEmbeddingsView POST request received ===")
        
        force = request.data.get('force', False)
        
        try:
            # Get properties that need embeddings
            if force:
                properties = Property.objects.all()
                message = f"Regenerating embeddings for all {properties.count()} properties..."
            else:
                properties = Property.objects.filter(embedding__isnull=True)
                message = f"Generating embeddings for {properties.count()} properties without embeddings..."
            
            logger.info(message)
            
            if not properties.exists():
                total_properties = Property.objects.count()
                return Response({
                    'status': 'success',
                    'message': 'All properties already have embeddings',
                    'total_properties': total_properties,
                    'with_embeddings': total_properties,
                    'coverage_percent': 100.0
                }, status=status.HTTP_200_OK)
            
            success_count = 0
            error_count = 0
            errors = []
            
            for property_obj in properties:
                try:
                    logger.info(f"Generating embedding for property {property_obj.id}...")
                    embedding = generate_property_embedding(property_obj)
                    
                    if embedding:
                        property_obj.embedding = embedding
                        property_obj.save(update_fields=['embedding'])
                        success_count += 1
                        logger.info(f"✅ Generated embedding for {property_obj.id}")
                    else:
                        error_count += 1
                        errors.append({'property_id': str(property_obj.id), 'error': 'No embedding generated'})
                        logger.warning(f"⚠️  No embedding generated for {property_obj.id}")
                        
                except Exception as e:
                    error_count += 1
                    errors.append({'property_id': str(property_obj.id), 'error': str(e)})
                    logger.error(f"❌ Error generating embedding for {property_obj.id}: {e}")
            
            # Get final statistics
            total_properties = Property.objects.count()
            with_embeddings = Property.objects.filter(embedding__isnull=False).count()
            coverage = (with_embeddings / total_properties * 100) if total_properties > 0 else 0
            
            logger.info(f"✅ Embedding generation complete!")
            logger.info(f"   Success: {success_count}, Errors: {error_count}")
            logger.info(f"   Coverage: {with_embeddings}/{total_properties} ({coverage:.1f}%)")
            
            return Response({
                'status': 'success',
                'message': 'Embedding generation complete',
                'total_properties': total_properties,
                'with_embeddings': with_embeddings,
                'coverage_percent': round(coverage, 1),
                'processed': success_count + error_count,
                'success': success_count,
                'errors': error_count,
                'error_details': errors[:10] if errors else []
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error in GenerateEmbeddingsView: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to generate embeddings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateGoogleSheetTemplateView(APIView):
    """
    Endpoint to create a new Google Sheet template.
    
    POST /ingest/create-sheet-template/
    {
        "title": "My Properties - January 2026"
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create a new Google Sheet template."""
        
        title = request.data.get('title', 'Property Ingestion Template')
        
        try:
            sheets_service = GoogleSheetsService()
            spreadsheet_id = sheets_service.create_template_sheet(title=title)
            
            return Response({
                'status': 'success',
                'spreadsheet_id': spreadsheet_id,
                'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit',
                'message': 'Template created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating Google Sheet template: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to create template: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelBatchView(APIView):
    """
    Endpoint to cancel ongoing batch processing.
    
    POST /ingest/cancel-batch/
    {
        "batch_id": "batch-1234567890"
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Cancel batch processing."""
        
        batch_id = request.data.get('batch_id')
        
        if not batch_id:
            return Response(
                {'error': 'batch_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"🛑 Cancellation requested for batch: {batch_id}")
        
        # Try to cancel any async tasks if they exist
        cancelled_tasks = 0
        try:
            from django.core.cache import cache
            from celery import current_app
            
            # Get task IDs associated with this batch
            task_ids = cache.get(f'batch_{batch_id}_tasks', [])
            
            if task_ids:
                for task_id in task_ids:
                    try:
                        current_app.control.revoke(task_id, terminate=True)
                        cancelled_tasks += 1
                        logger.info(f"✅ Cancelled task: {task_id}")
                    except Exception as e:
                        logger.error(f"Error cancelling task {task_id}: {e}")
                
                # Clear from cache
                cache.delete(f'batch_{batch_id}_tasks')
            else:
                logger.info("No async tasks found for this batch")
        
        except ImportError:
            # Celery not configured, which is fine for synchronous processing
            logger.info("Celery not available, batch was processed synchronously")
        except Exception as e:
            logger.error(f"Error cancelling tasks: {e}", exc_info=True)
        
        return Response({
            'status': 'cancelled',
            'batch_id': batch_id,
            'cancelled_tasks': cancelled_tasks,
            'message': f'Batch {batch_id} cancellation processed'
        }, status=status.HTTP_200_OK)
