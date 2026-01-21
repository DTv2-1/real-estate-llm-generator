"""
Transportation and Local Tips content type modules (simplified).
For full prompts, see content_types.py (legacy) - to be migrated later.
"""

from ..base import ContentTypeConfig


class TransportationConfig(ContentTypeConfig):
    KEY = 'transportation'
    LABEL = 'Transporte'
    ICON = '🚗'
    DESCRIPTION = 'Extrae información de transporte: rutas, costos, horarios, opciones disponibles.'
    DOMAINS = ['rome2rio', 'uber.com', 'lyft.com', 'bus.com']
    KEYWORDS = ['transport', 'transporte', 'bus', 'taxi', 'shuttle', 'route', 'schedule']
    CRITICAL_FIELDS = ['description', 'price_usd', 'duration_hours']
    ALLOWED_FIELDS = ['transport_name', 'transport_type', 'route', 'price_usd', 'duration_hours']


class LocalTipsConfig(ContentTypeConfig):
    KEY = 'local_tips'
    LABEL = 'Tips Locales / Consejos'
    ICON = '💡'
    DESCRIPTION = 'Extrae consejos prácticos: seguridad, costos, qué evitar, costumbres locales.'
    DOMAINS = ['wikivoyage', 'lonelyplanet', 'nomadicmatt']
    KEYWORDS = ['tip', 'tips', 'consejos', 'advice', 'local', 'safety', 'avoid']
    CRITICAL_FIELDS = ['description', 'practical_advice']
    ALLOWED_FIELDS = ['tip_title', 'category', 'location', 'description', 'practical_advice']
