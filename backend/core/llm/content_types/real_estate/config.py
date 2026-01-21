"""
Configuration for Real Estate content type.
"""

from ..base import ContentTypeConfig


class RealEstateConfig(ContentTypeConfig):
    """Configuration for real estate property content type."""
    
    KEY = 'real_estate'
    LABEL = 'Propiedad / Real Estate'
    ICON = '🏠'
    DESCRIPTION = 'Extrae información de propiedades inmobiliarias: precio, ubicación, características físicas, amenidades.'
    
    DOMAINS = [
        'brevitas.com',
        'coldwellbanker',
        'coldwellbankercostarica.com',
        'encuentra24.com',
        'century21',
        'remax',
        'properati',
        'mercadolibre',
        'olx',
    ]
    
    KEYWORDS = [
        'bedroom', 'bedrooms', 'habitaciones', 'recámaras',
        'bathroom', 'bathrooms', 'baños',
        'sqft', 'square feet', 'm2', 'm²', 'metros cuadrados',
        'property', 'propiedad', 'casa', 'house', 'apartment', 'apartamento',
        'for sale', 'venta', 'for rent', 'alquiler',
        'lot size', 'terreno', 'land',
    ]
    
    CRITICAL_FIELDS = [
        'description',
        'price',
        'bedrooms',
        'bathrooms',
    ]
    
    ALLOWED_FIELDS = [
        'property_name', 'property_type',
    ]
