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

from .schemas import PropertyData

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
        
        if not api_key:
            logger.error("❌ OPENAI_API_KEY is empty! Check environment variables.")
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = settings.OPENAI_MODEL_CHAT
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = 0.1  # Low temperature for consistent extraction
    
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
        
        # 2. Property details sections (common patterns)
        detail_patterns = [
            {'class': lambda x: x and ('show__' in x or 'product' in x or 'detail' in x or 'property' in x)},
            {'id': lambda x: x and ('detail' in x.lower() or 'overview' in x.lower())},
            {'class': lambda x: x and any(word in str(x).lower() for word in ['price', 'bedroom', 'bathroom', 'sqft', 'acres', 'lot'])},
        ]
        
        for pattern in detail_patterns:
            elements = soup.find_all(**pattern)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 10:  # Skip very short snippets
                    important_text.append(text)
        
        # 3. Structured data (JSON-LD, microdata)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                important_text.append(f"STRUCTURED DATA: {script.string}")
        
        # 4. Description/content paragraphs
        paragraphs = soup.find_all('p', class_=lambda x: x and ('description' in str(x).lower() or 'copy' in str(x).lower()))
        for p in paragraphs:
            text = p.get_text(separator=' ', strip=True)
            if len(text) > 50:  # Skip short paragraphs
                important_text.append(f"DESCRIPTION: {text}")
        
        # 5. All remaining text as fallback
        if not important_text:
            # If no structured sections found, get all text
            important_text.append(soup.get_text(separator=' ', strip=True))
        
        # Combine all extracted text
        combined = '\n\n'.join(important_text)
        
        # Remove excessive whitespace
        combined = ' '.join(combined.split())
        
        # Truncate if still too long (max ~100K chars for better coverage)
        if len(combined) > 100000:
            combined = combined[:100000] + "...[truncated]"
        
        return combined
    
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
        
        try:
            logger.info("Starting LLM property extraction with Structured Outputs...")
            
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data extraction specialist. Extract the following property information."},
                    {"role": "user", "content": prompt}
                ],
                response_format=PropertyData,
            )
            
            # Extract parsed Pydantic model
            property_data = completion.choices[0].message.parsed
            
            if not property_data:
                 raise ExtractionError("LLM returned empty parsed data")

            logger.info(f"LLM extraction completed. Tokens used: {completion.usage.total_tokens}")
            
            # Convert to dictionary using model_dump()
            validated_data = property_data.model_dump()
            
            # Handle decimals (Pydantic models use float/int, convert relevant fields to Decimal if needed by Django)
            # note: Pydantic v2 model_dump returns native python types. 
            # If downstream expects Decimal, we might need manual conversion or Pydantic config.
            # For now, let's keep it simple and convert essential financial/area fields if needed, 
            # but usually float is fine until save time.
            
            # Store field-level evidence in a separate dictionary as per original format
            evidence_fields = {}
            for key, value in validated_data.items():
                if key.endswith('_evidence') and value:
                    field_name = key.replace('_evidence', '')
                    evidence_fields[field_name] = value
            
            validated_data['field_confidence'] = evidence_fields
            validated_data['extracted_at'] = timezone.now()
            
            # Add metadata
            validated_data['source_url'] = url
            validated_data['raw_html'] = html[:10000]  # Store first 10K chars
            validated_data['tokens_used'] = completion.usage.total_tokens
            
            logger.info(f"Extraction successful. Confidence: {validated_data.get('extraction_confidence')}")
            
            return validated_data
            
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
