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

from .prompts import PROPERTY_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass


class PropertyExtractor:
    """
    Extract structured property data from unstructured HTML/text using LLM.
    """
    
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        logger.info(f"🔑 OPENAI_API_KEY configured: {'Yes' if api_key else 'No'}")
        logger.info(f"🔑 API Key length: {len(api_key) if api_key else 0} chars")
        logger.info(f"🔑 API Key preview: {api_key[:10]}..." if api_key and len(api_key) > 10 else "🔑 API Key: EMPTY or TOO SHORT")
        
        if not api_key:
            logger.error("❌ OPENAI_API_KEY is empty! Check environment variables.")
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = settings.OPENAI_MODEL_CHAT
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = 0.1  # Low temperature for consistent extraction
    
    def _clean_content(self, content: str) -> str:
        """Clean and truncate content for LLM processing."""
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Truncate if too long (max ~15K tokens = ~60K chars)
        if len(content) > 60000:
            content = content[:60000] + "...[truncated]"
        
        return content
    
    def _validate_extraction(self, data: Dict) -> Dict:
        """Validate and clean extracted data."""
        validated = {}
        
        # Handle price
        if data.get('price_usd'):
            try:
                validated['price_usd'] = Decimal(str(data['price_usd']))
            except (ValueError, TypeError):
                validated['price_usd'] = None
        
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
        
        # Handle strings
        for field in ['property_name', 'property_type', 'location', 'description',
                     'listing_id', 'internal_property_id', 'listing_status']:
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
    
    def extract_from_html(self, html: str, url: Optional[str] = None) -> Dict:
        """
        Extract property data from HTML content.
        
        Args:
            html: HTML content to extract from
            url: Optional source URL
            
        Returns:
            Dictionary with extracted property data
            
        Raises:
            ExtractionError: If extraction fails
        """
        
        # Clean content
        content = self._clean_content(html)
        
        # Prepare prompt
        prompt = PROPERTY_EXTRACTION_PROMPT.format(content=content)
        
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
            
            # Validate and clean
            validated_data = self._validate_extraction(extracted_data)
            
            # Add metadata
            validated_data['source_url'] = url
            validated_data['raw_html'] = html[:10000]  # Store first 10K chars
            validated_data['tokens_used'] = response.usage.total_tokens
            
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
    extractor = PropertyExtractor()
    return extractor.extract_from_html(content, url=url)
