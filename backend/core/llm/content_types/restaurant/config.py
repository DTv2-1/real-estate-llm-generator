"""
Configuration for Restaurant content type.
"""

from ..base import ContentTypeConfig


class RestaurantConfig(ContentTypeConfig):
    """Configuration for restaurant/dining content type."""
    
    KEY = 'restaurant'
    LABEL = 'Restaurante / Comida'
    ICON = '🍴'
    DESCRIPTION = 'Extrae información de restaurantes: tipo de cocina, rango de precios, platillos destacados, horarios.'
    
    DOMAINS = [
        'yelp.com',
        'zomato.com',
        'opentable.com',
        'tripadvisor',
        'happycow.net',
    ]
    
    KEYWORDS = [
        'restaurant', 'restaurante',
        'menu', 'menú',
        'cuisine', 'cocina',
        'dish', 'dishes', 'platillos', 'platos',
        'reservation', 'reserva', 'reservations',
        'dining', 'comida',
        'chef',
        'hours', 'horario',
        'price range', 'rango de precio',
    ]
    
    # Fields critical for web search
    CRITICAL_FIELDS = [
        'description',
        'price_range',
        'signature_dishes',
        'amenities',
        'atmosphere',
    ]
    
    # Fields allowed in validation (15 campos - fix del bug reportado)
    ALLOWED_FIELDS = [
        'restaurant_name', 'cuisine_type', 'opening_hours',
        'price_range', 'dress_code', 'reservation_required',
        'rating', 'number_of_reviews', 'contact_phone',
        'signature_dishes', 'atmosphere', 'dietary_options',
        'special_experiences', 'average_price_per_person',
        'parking_available',
    ]
