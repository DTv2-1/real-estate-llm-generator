"""
Embedding generation for semantic search.
Uses OpenAI embeddings API to create vector representations of property data.
"""

import logging
from typing import List, Optional
import openai
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding vector for given text using OpenAI API.
    
    Args:
        text: Text content to embed
        
    Returns:
        List of floats representing the embedding vector, or None if error
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for embedding generation")
        return None
    
    try:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.error("OPENAI_API_KEY not configured")
            return None
        
        client = openai.OpenAI(api_key=api_key)
        
        # Get embedding model from settings (default to text-embedding-3-small)
        model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        logger.info(f"Generating embedding with model: {model}")
        logger.info(f"Text length: {len(text)} chars")
        
        # Truncate text if too long (max 8191 tokens ≈ 32,000 chars)
        if len(text) > 32000:
            logger.warning(f"Text too long ({len(text)} chars), truncating to 32,000")
            text = text[:32000]
        
        # Call OpenAI API
        response = client.embeddings.create(
            model=model,
            input=text
        )
        
        # Extract embedding vector
        embedding = response.data[0].embedding
        
        logger.info(f"✓ Embedding generated successfully (dimension: {len(embedding)})")
        
        return embedding
        
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating embedding: {e}", exc_info=True)
        return None


def generate_property_embedding(property_obj) -> Optional[List[float]]:
    """
    Generate embedding for a Property object.
    Combines all relevant text fields into searchable content.
    
    Args:
        property_obj: Property model instance
        
    Returns:
        Embedding vector or None
    """
    try:
        # Build comprehensive text for embedding
        parts = []
        
        # Property name and description
        if property_obj.property_name:
            parts.append(f"Property: {property_obj.property_name}")
        
        if property_obj.description:
            parts.append(f"Description: {property_obj.description}")
        
        # Location info
        location_parts = []
        if property_obj.city:
            location_parts.append(property_obj.city)
        if property_obj.province:
            location_parts.append(property_obj.province)
        if property_obj.country:
            location_parts.append(property_obj.country)
        
        if location_parts:
            parts.append(f"Location: {', '.join(location_parts)}")
        
        if property_obj.address:
            parts.append(f"Address: {property_obj.address}")
        
        # Property details
        if property_obj.property_type:
            parts.append(f"Type: {property_obj.property_type}")
        
        if property_obj.bedrooms:
            parts.append(f"Bedrooms: {property_obj.bedrooms}")
        
        if property_obj.bathrooms:
            parts.append(f"Bathrooms: {property_obj.bathrooms}")
        
        if property_obj.area_m2:
            parts.append(f"Area: {property_obj.area_m2} m²")
        
        if property_obj.lot_size_m2:
            parts.append(f"Lot size: {property_obj.lot_size_m2} m²")
        
        # Price
        if property_obj.price_usd:
            parts.append(f"Price: ${property_obj.price_usd:,.2f} USD")
        
        # Amenities
        if property_obj.amenities:
            amenities_text = ", ".join(property_obj.amenities)
            parts.append(f"Amenities: {amenities_text}")
        
        # Combine all parts
        text = "\n".join(parts)
        
        logger.info(f"Generating embedding for property: {property_obj.property_name}")
        logger.info(f"Combined text length: {len(text)} chars")
        
        # Generate embedding
        return generate_embedding(text)
        
    except Exception as e:
        logger.error(f"Error generating property embedding: {e}", exc_info=True)
        return None


def batch_generate_embeddings(texts: List[str], model: str = None) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts in a single API call.
    More efficient for bulk operations.
    
    Args:
        texts: List of text strings to embed
        model: Embedding model to use (optional)
        
    Returns:
        List of embedding vectors (same order as input)
    """
    if not texts:
        return []
    
    try:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.error("OPENAI_API_KEY not configured")
            return [None] * len(texts)
        
        client = openai.OpenAI(api_key=api_key)
        
        if not model:
            model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        logger.info(f"Batch generating {len(texts)} embeddings with model: {model}")
        
        # Filter out empty texts
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text[:32000])  # Truncate if needed
                valid_indices.append(i)
        
        if not valid_texts:
            logger.warning("No valid texts to embed")
            return [None] * len(texts)
        
        # Call OpenAI API with batch
        response = client.embeddings.create(
            model=model,
            input=valid_texts
        )
        
        # Build result list with None for invalid texts
        results = [None] * len(texts)
        for i, embedding_obj in enumerate(response.data):
            original_index = valid_indices[i]
            results[original_index] = embedding_obj.embedding
        
        logger.info(f"✓ Batch embeddings generated successfully")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch embedding generation: {e}", exc_info=True)
        return [None] * len(texts)
