"""
Utility to detect source website from URL.
"""

from urllib.parse import urlparse


def detect_source_website(url: str) -> str:
    """
    Detect source website from URL.
    
    Args:
        url: Property listing URL
        
    Returns:
        Source website identifier (encuentra24, crrealestate, coldwellbanker, other)
    """
    if not url:
        return 'other'
    
    try:
        domain = urlparse(url).netloc.lower()
        
        # Map domains to source website identifiers
        if 'encuentra24' in domain:
            return 'encuentra24'
        elif 'crrealestate' in domain or 'cr-realestate' in domain:
            return 'crrealestate'
        elif 'coldwellbanker' in domain:
            return 'coldwellbanker'
        else:
            return 'other'
            
    except Exception:
        return 'other'
