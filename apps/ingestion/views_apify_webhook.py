"""
Django webhook endpoint to receive data from Apify Actor
"""
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from apps.properties.models import Property
from apps.documents.models import Document

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def apify_webhook(request):
    """
    Receive extracted property data from Apify Actor
    
    Expected payload:
    {
        "url": "https://...",
        "title": "Property Title",
        "extracted_data": {
            "price": 250000,
            "currency": "USD",
            "beds": 3,
            "baths": 2,
            "size_m2": 150,
            "location": "Tamarindo",
            "property_type": "house",
            "status": "sale"
        },
        "confidence": {...},
        "evidence": {...},
        "scraped_at": "2026-01-07T12:00:00Z",
        "raw_html_key": "raw_12345"
    }
    """
    
    try:
        # Parse JSON payload
        data = json.loads(request.body)
        
        url = data.get('url')
        title = data.get('title')
        extracted = data.get('extracted_data', {})
        confidence = data.get('confidence', {})
        scraped_at = data.get('scraped_at')
        raw_html_key = data.get('raw_html_key')
        
        if not url:
            return JsonResponse({'error': 'Missing URL'}, status=400)
        
        logger.info(f'Received data from Apify for {url}')
        
        # Create or update Property
        property_obj, created = Property.objects.update_or_create(
            source_url=url,
            defaults={
                'title': title,
                'price': extracted.get('price'),
                'currency': extracted.get('currency', 'USD'),
                'bedrooms': extracted.get('beds'),
                'bathrooms': extracted.get('baths'),
                'size_m2': extracted.get('size_m2'),
                'lot_size_m2': extracted.get('lot_m2'),
                'location': extracted.get('location'),
                'property_type': extracted.get('property_type'),
                'listing_type': extracted.get('status'),
                'description': extracted.get('description'),
                'amenities': extracted.get('amenities') or [],
                'metadata': {
                    'confidence': confidence,
                    'evidence': data.get('evidence', {}),
                    'scraped_at': scraped_at,
                    'raw_html_key': raw_html_key,
                    'extraction_status': data.get('extraction_status')
                }
            }
        )
        
        # Create Document record for raw HTML reference
        if raw_html_key:
            Document.objects.update_or_create(
                property=property_obj,
                doc_type='raw_html',
                defaults={
                    'content': f'Raw HTML stored in Apify: {raw_html_key}',
                    'metadata': {
                        'apify_key': raw_html_key,
                        'actor_run_id': data.get('actor_run_id')
                    }
                }
            )
        
        logger.info(f'{"Created" if created else "Updated"} property: {property_obj.id}')
        
        return JsonResponse({
            'status': 'success',
            'property_id': property_obj.id,
            'created': created
        })
        
    except json.JSONDecodeError:
        logger.error('Invalid JSON in request body')
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    except Exception as e:
        logger.error(f'Error processing Apify webhook: {e}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
