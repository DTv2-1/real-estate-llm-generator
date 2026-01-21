"""
Configuration for Tour content type.
"""

from ..base import ContentTypeConfig


class TourConfig(ContentTypeConfig):
    """Configuration for tour/activity content type."""
    
    KEY = 'tour'
    LABEL = 'Tour / Actividad'
    ICON = '🗺️'
    DESCRIPTION = 'Extrae información de tours y actividades: tipo, duración, precio, qué incluye, nivel de dificultad.'
    
    DOMAINS = [
        'viator.com',
        'getyourguide.com',
        'tripadvisor',
        'airbnbexperiences',
        'klook.com',
        'costarica.org',  # Costa Rica official tourism
    ]
    
    KEYWORDS = [
        'tour', 'tours', 'excursion', 'excursiones', 'excursions',
        'activity', 'activities', 'actividades',
        'adventure', 'adventures', 'aventura',
        'experience', 'experiences', 'experiencias',
        'duration', 'duración',
        'guide', 'guía', 'guided',
        'included', 'incluye', 'includes',
        'pickup', 'recogida',
        'participants', 'participantes',
        'difficulty', 'dificultad',
        'booking', 'reserva', 'book',
        'itinerary', 'itinerario',
        'wildlife', 'nature', 'naturaleza',
        'zip line', 'canopy', 'rafting', 'hiking',
    ]
    
    # Fields critical for web search
    CRITICAL_FIELDS = [
        'description',
        'price_usd',
        'duration_hours',
        'included_items',
    ]
    
    # Fields allowed in validation
    ALLOWED_FIELDS = [
        'tour_name', 'tour_type', 'duration_hours', 'difficulty_level',
        'included_items', 'excluded_items', 'max_participants',
        'languages_available', 'pickup_included', 'minimum_age',
        'cancellation_policy', 'schedules', 'what_to_bring',
        'check_in_time', 'restrictions',
    ]
