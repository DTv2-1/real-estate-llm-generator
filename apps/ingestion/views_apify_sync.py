"""
Django view to fetch HTML from Apify and extract data with OpenAI
Architecture: Apify (scraping) → Django (fetch HTML + OpenAI extraction) → PostgreSQL
"""

import json
import logging
from typing import Dict, Optional

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apify_client import ApifyClient
from openai import OpenAI
from bs4 import BeautifulSoup

from apps.properties.models import Property
from apps.documents.models import Document

logger = logging.getLogger(__name__)


def extract_with_openai(html_content: str, url: str) -> Dict:
    """
    Extract structured property data from HTML using OpenAI API.
    
    Args:
        html_content: Raw HTML string from Apify
        url: Source URL for context
        
    Returns:
        Dictionary with extracted data, confidence scores, and evidence
    """
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(['script', 'style', 'noscript', 'iframe']):
        script.decompose()
    
    # Get clean text content
    text = soup.get_text(separator='\n', strip=True)
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
    text_content = '\n'.join(chunk for chunk in chunks if chunk)
    
    # Truncate if too long (OpenAI has token limits)
    max_chars = 8000  # ~2000 tokens for gpt-4o-mini
    if len(text_content) > max_chars:
        text_content = text_content[:max_chars] + "..."
    
    logger.info(f'Extracted {len(text_content)} chars of text from HTML')
    
    # Call OpenAI API
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        extraction_prompt = f"""
Extract real estate property information from this webpage text.

Return a JSON object with this exact structure:
{{
  "price": number or null,
  "currency": "USD" or "CRC" or null,
  "beds": number or null,
  "baths": number or null,
  "size_m2": number or null,
  "lot_m2": number or null,
  "location": string or null,
  "property_type": "house" or "apartment" or "land" or "commercial" or null,
  "status": "sale" or "rent" or null,
  "title": string or null,
  "description": string or null,
  "amenities": [list of strings] or null,
  "confidence": {{
    "price": 0.0 to 1.0,
    "location": 0.0 to 1.0,
    "beds": 0.0 to 1.0
  }},
  "evidence": {{
    "price": "exact quote from text",
    "location": "exact quote from text"
  }}
}}

IMPORTANT:
- If a field cannot be determined, use null
- Include confidence scores (0.0 to 1.0) for key fields
- Provide evidence as exact quotes from the text
- Do NOT hallucinate or guess data

Webpage URL: {url}

Webpage Text:
{text_content}

Return ONLY the JSON object, no markdown, no explanations:
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a real estate data extraction specialist. Extract structured data from property listings and return valid JSON only. Never hallucinate data."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        # Parse JSON response
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith('```'):
            # Extract content between ```json and ```
            parts = content.split('```')
            for part in parts:
                if part.strip().startswith('json'):
                    content = part[4:].strip()
                    break
                elif part.strip() and not part.strip().startswith('json'):
                    content = part.strip()
                    break
        
        extracted_data = json.loads(content)
        
        logger.info(f'Successfully extracted data from {url}: {extracted_data.get("title", "Unknown")}')
        
        return {
            'extraction_status': 'success',
            'extracted_data': extracted_data,
            'model': 'gpt-4o-mini',
            'tokens_used': response.usage.total_tokens
        }
        
    except json.JSONDecodeError as e:
        logger.error(f'Failed to parse OpenAI response as JSON: {e}')
        logger.error(f'Raw response: {content[:500]}')
        return {
            'extraction_status': 'error',
            'error': 'invalid_json',
            'raw_response': content[:500]
        }
    except Exception as e:
        logger.error(f'OpenAI extraction failed: {e}')
        return {
            'extraction_status': 'error',
            'error': str(e)
        }


@csrf_exempt
@require_http_methods(["POST"])
def sync_apify_dataset(request):
    """
    Fetch dataset from Apify, get HTML, extract with OpenAI, save to PostgreSQL.
    
    POST body:
    {
        "dataset_id": "abc123",  # Apify dataset ID
        "actor_run_id": "xyz789"  # Optional: Apify run ID for reference
    }
    """
    try:
        data = json.loads(request.body)
        dataset_id = data.get('dataset_id')
        actor_run_id = data.get('actor_run_id')
        
        if not dataset_id:
            return JsonResponse({'error': 'dataset_id is required'}, status=400)
        
        # Initialize Apify client
        apify_token = getattr(settings, 'APIFY_TOKEN', None)
        if not apify_token:
            return JsonResponse({'error': 'APIFY_TOKEN not configured'}, status=500)
        
        client = ApifyClient(apify_token)
        
        # Fetch dataset items
        dataset = client.dataset(dataset_id)
        items = list(dataset.iterate_items())
        
        logger.info(f'Fetched {len(items)} items from Apify dataset {dataset_id}')
        
        processed = 0
        errors = 0
        
        for item in items:
            url = item.get('url')
            html_key = item.get('html_key')
            
            if not url or not html_key:
                logger.warning(f'Skipping item without url or html_key: {item}')
                errors += 1
                continue
            
            try:
                # Fetch HTML from Apify Key-Value Store
                # The HTML is stored in the same run's default KV store
                run = client.run(actor_run_id) if actor_run_id else None
                kv_store_id = run.get('defaultKeyValueStoreId') if run else None
                
                if not kv_store_id:
                    # Try to get KV store from actor run ID in item
                    run_id = item.get('actor_run_id')
                    if run_id:
                        run = client.run(run_id)
                        kv_store_id = run.get('defaultKeyValueStoreId')
                
                if not kv_store_id:
                    logger.error(f'Cannot find Key-Value Store for {url}')
                    errors += 1
                    continue
                
                # Fetch HTML from Key-Value Store
                kv_store = client.key_value_store(kv_store_id)
                html_record = kv_store.get_record(html_key)
                
                if not html_record or not html_record.get('value'):
                    logger.error(f'HTML not found in KV store for key {html_key}')
                    errors += 1
                    continue
                
                html_content = html_record['value']
                logger.info(f'Fetched HTML for {url} ({len(html_content)} bytes)')
                
                # Extract data with OpenAI
                extraction_result = extract_with_openai(html_content, url)
                
                if extraction_result['extraction_status'] != 'success':
                    logger.error(f'Extraction failed for {url}: {extraction_result.get("error")}')
                    errors += 1
                    continue
                
                extracted = extraction_result['extracted_data']
                
                # Save to PostgreSQL
                property_obj, created = Property.objects.update_or_create(
                    source_url=url,
                    defaults={
                        'title': extracted.get('title'),
                        'description': extracted.get('description'),
                        'price': extracted.get('price'),
                        'currency': extracted.get('currency', 'USD'),
                        'beds': extracted.get('beds'),
                        'baths': extracted.get('baths'),
                        'size_m2': extracted.get('size_m2'),
                        'lot_m2': extracted.get('lot_m2'),
                        'location': extracted.get('location'),
                        'property_type': extracted.get('property_type'),
                        'status': extracted.get('status', 'sale'),
                        'metadata': {
                            'confidence': extracted.get('confidence', {}),
                            'evidence': extracted.get('evidence', {}),
                            'extraction_model': extraction_result.get('model'),
                            'tokens_used': extraction_result.get('tokens_used'),
                            'apify_dataset_id': dataset_id,
                            'apify_html_key': html_key
                        }
                    }
                )
                
                # Create Document record linking to raw HTML in Apify
                Document.objects.update_or_create(
                    property=property_obj,
                    source_type='apify',
                    defaults={
                        'content': html_content[:5000],  # Store snippet
                        'metadata': {
                            'apify_kv_store_id': kv_store_id,
                            'apify_html_key': html_key,
                            'full_html_url': f'https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/{html_key}'
                        }
                    }
                )
                
                action = 'created' if created else 'updated'
                logger.info(f'Successfully {action} property: {extracted.get("title")} ({url})')
                processed += 1
                
            except Exception as e:
                logger.error(f'Error processing {url}: {e}', exc_info=True)
                errors += 1
                continue
        
        return JsonResponse({
            'status': 'success',
            'dataset_id': dataset_id,
            'total_items': len(items),
            'processed': processed,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f'Sync failed: {e}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
