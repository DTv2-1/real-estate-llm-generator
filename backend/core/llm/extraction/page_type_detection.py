"""
Módulo para detectar el tipo de página: específica (un solo ítem) o general (guía/listado).
Utiliza Web Search para clasificación inteligente.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from django.conf import settings

# Import WebSearchService
from .web_search import WebSearchService

logger = logging.getLogger(__name__)


class PageTypeDetector:
    """
    Detecta si una página es específica (un solo ítem detallado) o general (guía/listado).
    
    Utiliza Web Search con contexto de URL y contenido para clasificación inteligente.
    """
    
    def __init__(self):
        """Initialize detector with Web Search service."""
        try:
            self.web_search = WebSearchService()
        except Exception as e:
            logger.warning(f"⚠️ No se pudo inicializar Web Search: {e}")
            self.web_search = None
    
    def detect_page_type(
        self,
        url: str,
        html_content: str,
        content_type: str = "unknown"
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detecta el tipo de página usando Web Search.
        
        Args:
            url: URL de la página
            html_content: Contenido HTML de la página
            content_type: Tipo de contenido (tour, restaurant, real_estate, etc.)
            
        Returns:
            Tupla de (page_type, confidence, metadata)
            - page_type: "specific" o "general"
            - confidence: float entre 0 y 1
            - metadata: dict con información adicional sobre la detección
        """
        logger.info(f"🔍 Detectando tipo de página para URL: {url}")
        
        metadata = {
            "url": url,
            "content_type": content_type,
            "method": "web_search"
        }
        
        # Preparar consulta para Web Search
        search_query = f"""Analyze this webpage and determine if it's a SPECIFIC page (single item with details) or a GENERAL page (guide/listing with multiple items).

URL: {url}
Content Type: {content_type}

Is this page showing:
- SPECIFIC: A single {content_type} with detailed information (e.g., one tour, one restaurant, one property)
- GENERAL: A guide, listing, or collection of multiple {content_type}s

Respond with only: "SPECIFIC" or "GENERAL" """
        
        try:
            # Verificar si Web Search está disponible
            if not self.web_search or not self.web_search.enabled:
                logger.info("⚠️ Web Search no disponible, usando fallback")
                return self._fallback_detection(url, content_type, metadata)
            
            # Usar Web Search para clasificación
            search_results = self.web_search.search(
                query=search_query,
                model="gpt-4o",
                country="PA"  # Panama
            )
            
            if not search_results or not search_results.get('answer'):
                logger.warning("⚠️ Web Search no retornó respuesta, usando fallback")
                return self._fallback_detection(url, content_type, metadata)
            
            # Parsear respuesta
            answer = search_results['answer'].strip().upper()
            
            if "SPECIFIC" in answer:
                page_type = "specific"
                confidence = 0.85
                logger.info(f"✅ Web Search detectó página específica: {url}")
            elif "GENERAL" in answer:
                page_type = "general"
                confidence = 0.85
                logger.info(f"✅ Web Search detectó página general: {url}")
            else:
                logger.warning(f"⚠️ Respuesta ambigua de Web Search: {answer}")
                return self._fallback_detection(url, content_type, metadata)
            
            metadata["web_search_answer"] = search_results['answer']
            metadata["sources_used"] = len(search_results.get('sources', []))
            
            return page_type, confidence, metadata
            
        except Exception as e:
            logger.error(f"❌ Error en Web Search: {str(e)}", exc_info=True)
            return self._fallback_detection(url, content_type, metadata)
    
    def _fallback_detection(
        self, 
        url: str, 
        content_type: str, 
        metadata: Dict[str, Any]
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detección de respaldo basada en patrones de URL simples.
        
        Args:
            url: URL de la página
            content_type: Tipo de contenido
            metadata: Metadata existente
            
        Returns:
            Tupla de (page_type, confidence, metadata)
        """
        logger.info("📋 Usando detección de respaldo por patrones de URL")
        
        url_lower = url.lower()
        
        # Patrones que indican página GENERAL
        general_patterns = [
            '/tours', '/experiences', '/activities',
            '/restaurants', '/dining', '/eat',
            '/properties', '/listings', '/search',
            '/guide', '/guides', '/directory',
            '/list', '/all', '/category',
            '/best-', '/top-', '/popular'
        ]
        
        # Patrones que indican página ESPECÍFICA
        specific_patterns = [
            '/tour/', '/experience/',
            '/restaurant/', '/venue/',
            '/property/', '/listing/',
            '-tour-', '-restaurant-', '-property-',
            '/map/',  # Rome2Rio specific routes
            '/s/',    # Rome2Rio alternate route format
        ]
        
        # Verificar patrones GENERAL
        for pattern in general_patterns:
            if pattern in url_lower:
                metadata["fallback_pattern"] = pattern
                metadata["fallback_type"] = "general"
                logger.info(f"✅ Patrón general detectado: {pattern}")
                return "general", 0.6, metadata
        
        # Verificar patrones ESPECÍFICO
        for pattern in specific_patterns:
            if pattern in url_lower:
                metadata["fallback_pattern"] = pattern
                metadata["fallback_type"] = "specific"
                logger.info(f"✅ Patrón específico detectado: {pattern}")
                return "specific", 0.6, metadata
        
        # Por defecto, asumir ESPECÍFICO (es más común y seguro)
        logger.info("⚠️ Sin patrones claros, asumiendo página específica por defecto")
        metadata["fallback_pattern"] = "default"
        metadata["fallback_type"] = "default_specific"
        return "specific", 0.5, metadata


def detect_page_type(url: str, html_content: str = "", content_type: str = "unknown") -> Dict[str, Any]:
    """
    Función de conveniencia para detectar tipo de página.
    
    Args:
        url: URL de la página
        html_content: Contenido HTML (opcional)
        content_type: Tipo de contenido
        
    Returns:
        Dict con:
        - page_type: "specific" o "general"
        - confidence: float entre 0 y 1
        - reasoning: str explicando la detección
        - method: str indicando el método usado
    """
    detector = PageTypeDetector()
    page_type, confidence, metadata = detector.detect_page_type(url, html_content, content_type)
    
    return {
        'page_type': page_type,
        'confidence': confidence,
        'reasoning': metadata.get('web_search_answer', metadata.get('fallback_pattern', 'Unknown')),
        'method': metadata.get('method', 'fallback'),
        'metadata': metadata
    }
