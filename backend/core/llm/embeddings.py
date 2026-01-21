"""
Embedding generation for all content types.
Uses OpenAI embeddings API to create vector representations of content data.
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


def generate_property_embedding(content_obj) -> Optional[List[float]]:
    """
    Generate embedding for any content object (Property, Restaurant, Tour, Transportation, etc).
    Combines all relevant text fields into searchable content.
    
    Args:
        content_obj: Any content model instance (Property, TransportationSpecific, etc)
        
    Returns:
        Embedding vector or None
    """
    try:
        # Build comprehensive text for embedding
        parts = []
        
        # Title (works for all content types via BaseContent)
        if hasattr(content_obj, 'title') and content_obj.title:
            parts.append(f"Title: {content_obj.title}")
        
        # For old Property model compatibility
        if hasattr(content_obj, 'property_name') and content_obj.property_name:
            parts.append(f"Property: {content_obj.property_name}")
        
        # Description (BaseContent field)
        if hasattr(content_obj, 'description') and content_obj.description:
            parts.append(f"Description: {content_obj.description}")
        
        # Location info (BaseContent fields)
        if hasattr(content_obj, 'location') and content_obj.location:
            parts.append(f"Location: {content_obj.location}")
        
        # Content-specific fields
        
        # Real Estate
        if hasattr(content_obj, 'property_type') and content_obj.property_type:
            parts.append(f"Type: {content_obj.property_type}")
        
        if hasattr(content_obj, 'bedrooms') and content_obj.bedrooms:
            parts.append(f"Bedrooms: {content_obj.bedrooms}")
        
        if hasattr(content_obj, 'bathrooms') and content_obj.bathrooms:
            parts.append(f"Bathrooms: {content_obj.bathrooms}")
        
        if hasattr(content_obj, 'square_meters') and content_obj.square_meters:
            parts.append(f"Area: {content_obj.square_meters} m²")
        
        # Restaurant
        if hasattr(content_obj, 'restaurant_name') and content_obj.restaurant_name:
            parts.append(f"Restaurant: {content_obj.restaurant_name}")
        
        if hasattr(content_obj, 'cuisine_type') and content_obj.cuisine_type:
            cuisine = ", ".join(content_obj.cuisine_type) if isinstance(content_obj.cuisine_type, list) else content_obj.cuisine_type
            parts.append(f"Cuisine: {cuisine}")
        
        # Tour
        if hasattr(content_obj, 'tour_name') and content_obj.tour_name:
            parts.append(f"Tour: {content_obj.tour_name}")
        
        if hasattr(content_obj, 'duration') and content_obj.duration:
            parts.append(f"Duration: {content_obj.duration}")
        
        if hasattr(content_obj, 'difficulty') and content_obj.difficulty:
            parts.append(f"Difficulty: {content_obj.difficulty}")
        
        # Transportation
        if hasattr(content_obj, 'route_name') and content_obj.route_name:
            parts.append(f"Route: {content_obj.route_name}")
        
        if hasattr(content_obj, 'departure_location') and content_obj.departure_location:
            parts.append(f"From: {content_obj.departure_location}")
        
        if hasattr(content_obj, 'arrival_location') and content_obj.arrival_location:
            parts.append(f"To: {content_obj.arrival_location}")
        
        if hasattr(content_obj, 'transport_type') and content_obj.transport_type:
            parts.append(f"Transport: {content_obj.transport_type}")
        
        # Price (many content types have price fields)
        if hasattr(content_obj, 'price_usd') and content_obj.price_usd:
            parts.append(f"Price: ${content_obj.price_usd:,.2f} USD")
        elif hasattr(content_obj, 'price_min') and content_obj.price_min:
            if hasattr(content_obj, 'price_max') and content_obj.price_max:
                parts.append(f"Price: ${content_obj.price_min:,.2f} - ${content_obj.price_max:,.2f} USD")
            else:
                parts.append(f"Price from: ${content_obj.price_min:,.2f} USD")
        
        # Amenities (Property and others)
        if hasattr(content_obj, 'amenities') and content_obj.amenities:
            amenities_text = ", ".join(content_obj.amenities)
            parts.append(f"Amenities: {amenities_text}")
        
        # Combine all parts
        text = "\n".join(parts)
        
        # Get object identifier for logging
        obj_name = getattr(content_obj, 'title', None) or getattr(content_obj, 'property_name', None) or str(content_obj.id)
        
        logger.info(f"Generating embedding for: {obj_name}")
        logger.info(f"Combined text length: {len(text)} chars")
        
        # Generate embedding
        return generate_embedding(text)
        
    except Exception as e:
        logger.error(f"Error generating content embedding: {e}", exc_info=True)
        return None
