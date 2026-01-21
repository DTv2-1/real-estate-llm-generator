"""
Local Tips content type configuration.
"""

from ..base import ContentTypeConfig


class LocalTipsConfig(ContentTypeConfig):
    """Configuration for local tips and travel advice content type."""
    
    KEY = 'local_tips'
    LABEL = 'Tips Locales / Consejos'
    ICON = '💡'
    DESCRIPTION = 'Extrae consejos prácticos: seguridad, costos, qué evitar, costumbres locales.'
    
    DOMAINS = [
        'wikivoyage',
        'lonelyplanet',
        'nomadicmatt',
        'reddit.com/r/travel',
    ]
    
    KEYWORDS = [
        'tip', 'tips', 'consejos',
        'advice', 'recomendación',
        'local', 'locals',
        'avoid', 'evitar',
        'safety', 'seguridad',
        'scam', 'estafa',
        'budget', 'presupuesto',
        'money', 'dinero',
        'customs', 'costumbres',
    ]
    
    CRITICAL_FIELDS = [
        'description',
        'practical_advice',
        'category',
    ]
    
    ALLOWED_FIELDS = [
        'tip_title',
        'category',
        'location',
        'description',
        'practical_advice',
        'cost_estimate',
        'best_time',
        'things_to_avoid',
        'local_customs',
        'emergency_contacts',
    ]
