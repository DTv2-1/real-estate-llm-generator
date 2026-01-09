"""
Site-specific HTML extractors.
Each extractor knows how to parse HTML from a specific real estate website.
"""

from .base import BaseExtractor
from .brevitas import BrevitasExtractor
from .encuentra24 import Encuentra24Extractor
from .coldwell_banker import ColdwellBankerExtractor

# Registry of extractors by domain
EXTRACTORS = {
    'brevitas.com': BrevitasExtractor,
    'encuentra24.com': Encuentra24Extractor,
    'coldwellbankercostarica.com': ColdwellBankerExtractor,
}

def get_extractor(url: str) -> BaseExtractor:
    """Get the appropriate extractor for a URL."""
    from urllib.parse import urlparse
    
    domain = urlparse(url).netloc
    # Remove www. prefix
    domain = domain.replace('www.', '')
    
    # Find matching extractor
    for pattern, extractor_class in EXTRACTORS.items():
        if pattern in domain:
            return extractor_class()
    
    # Default to base extractor (generic LLM-based)
    return BaseExtractor()

__all__ = [
    'BaseExtractor',
    'BrevitasExtractor',
    'Encuentra24Extractor',
    'ColdwellBankerExtractor',
    'get_extractor',
    'EXTRACTORS',
]
