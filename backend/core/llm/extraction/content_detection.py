"""
Content type detection using OpenAI web search.
Detects the type of content (real_estate, tour, restaurant, etc.) using web search + AI classification.
"""

import logging
from typing import Optional, Dict
from django.conf import settings

from ..content_types import CONTENT_TYPES

logger = logging.getLogger(__name__)


# ============================================================================
# MAIN DETECTION FUNCTION
# ============================================================================

def detect_content_type(
    url: str,
    html: str,
    user_override: Optional[str] = None,
    use_llm_fallback: bool = False
) -> Dict[str, any]:
    """
    Detect content type using web search.
    
    Detection strategy (in order):
    1. User override (if provided) - 100% confidence
    2. Web Search with GPT-4o-mini classification - fast, accurate, uses OpenAI Responses API
    3. Fallback to real_estate if web search disabled or fails
    
    Args:
        url: Source URL
        html: HTML content
        user_override: User-specified content type (highest priority)
        use_llm_fallback: Whether to use LLM as last resort (deprecated, kept for compatibility)
        
    Returns:
        Dict with:
            - content_type: Detected type key
            - confidence: Confidence score (0.0 to 1.0)
            - method: Detection method used
            - suggested_type: Best guess for UI pre-selection
            - reasoning: Explanation (only for web_search method)
            - sources: Web sources consulted (only for web_search method)
    """
    logger.info("=" * 80)
    logger.info("🔎 Starting content type detection")
    logger.info("=" * 80)
    
    # Strategy 1: User override (100% confidence)
    if user_override:
        if user_override in CONTENT_TYPES:
            logger.info(f"✅ Using user override: {user_override}")
            return {
                'content_type': user_override,
                'confidence': 1.0,
                'method': 'user_override',
                'suggested_type': user_override
            }
        else:
            logger.warning(f"⚠️ Invalid user override: {user_override}, ignoring")
    
    # Strategy 2: Web Search detection with GPT-4o-mini classification
    if getattr(settings, 'WEB_SEARCH_ENABLED', False):
        try:
            from .web_search import get_web_search_service
            
            web_search_service = get_web_search_service()
            
            logger.info("🌐 Using web search detection with AI classification...")
            detection_result = web_search_service.detect_content_type(url, html_preview=None)
            
            if detection_result['content_type'] != 'unknown':
                logger.info(f"✅ Web search detection: {detection_result['content_type']} ({detection_result['confidence']:.2%})")
                return {
                    'content_type': detection_result['content_type'],
                    'confidence': detection_result['confidence'],
                    'method': 'web_search',
                    'suggested_type': detection_result['content_type'],
                    'reasoning': detection_result.get('reasoning', ''),
                    'sources': detection_result.get('sources', [])
                }
            else:
                logger.warning("⚠️ Web search returned unknown type, using fallback")
        
        except Exception as e:
            logger.warning(f"⚠️ Web search detection failed: {e}, using fallback")
    else:
        logger.info("⚠️ Web search detection disabled (WEB_SEARCH_ENABLED=False)")
    
    # Fallback: Default to real_estate (original purpose)
    logger.warning("⚠️ Using fallback: defaulting to real_estate")
    return {
        'content_type': 'real_estate',
        'confidence': 0.5,
        'method': 'default_fallback',
        'suggested_type': 'real_estate'
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_content_type_label(content_type: str) -> str:
    """Get human-readable label for content type."""
    config = CONTENT_TYPES.get(content_type)
    return config['label'] if config else content_type


def get_content_type_icon(content_type: str) -> str:
    """Get icon for content type."""
    config = CONTENT_TYPES.get(content_type)
    return config['icon'] if config else '📄'
