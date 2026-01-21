"""
Serializers for new content models (GENERAL & SPECIFIC).
"""

from rest_framework import serializers
from .models_content import (
    RealEstateGeneral,
    RealEstateSpecific,
    RestaurantGeneral,
    RestaurantSpecific,
    TourGeneral,
    TourSpecific,
    TransportationGeneral,
    TransportationSpecific,
    LocalTipsGeneral,
    LocalTipsSpecific,
    ContentImage,
)


# =============================================================================
# BASE SERIALIZER WITH COMMON FIELDS
# =============================================================================

class BaseContentSerializer(serializers.ModelSerializer):
    """Base serializer with common fields for all content types."""
    
    class Meta:
        fields = [
            'id',
            'title',
            'description',
            'location',
            'latitude',
            'longitude',
            'source_website',
            'source_url',
            'extraction_confidence',
            'field_confidence',
            'extracted_at',
            'user_roles',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'extracted_at', 'created_at', 'updated_at']


# =============================================================================
# REAL ESTATE SERIALIZERS
# =============================================================================

class RealEstateGeneralSerializer(BaseContentSerializer):
    """Serializer for RealEstateGeneral (market guides)."""
    
    class Meta(BaseContentSerializer.Meta):
        model = RealEstateGeneral
        fields = BaseContentSerializer.Meta.fields + [
            'destination',
            'total_properties',
            'price_range_min',
            'price_range_max',
            'property_types',
            'popular_areas',
        ]


class RealEstateSpecificSerializer(BaseContentSerializer):
    """Serializer for RealEstateSpecific (individual properties)."""
    
    class Meta(BaseContentSerializer.Meta):
        model = RealEstateSpecific
        fields = BaseContentSerializer.Meta.fields + [
            'property_type',
            'status',
            'price_usd',
            'bedrooms',
            'bathrooms',
            'square_meters',
            'lot_size_m2',
            'amenities',
            'year_built',
            'parking_spaces',
            'hoa_fee_monthly',
            'property_tax_annual',
            'listing_id',
            'date_listed',
        ]


# =============================================================================
# RESTAURANT SERIALIZERS
# =============================================================================

class RestaurantGeneralSerializer(BaseContentSerializer):
    """Serializer for RestaurantGeneral (restaurant guides)."""
    
    class Meta(BaseContentSerializer.Meta):
        model = RestaurantGeneral
        fields = BaseContentSerializer.Meta.fields + [
            'destination',
            'total_restaurants',
            'cuisine_types',
            'price_ranges',
            'neighborhoods',
        ]


class RestaurantSpecificSerializer(BaseContentSerializer):
    """Serializer for RestaurantSpecific (individual restaurants)."""
    
    # Add computed fields from field_confidence
    signature_dishes = serializers.SerializerMethodField()
    atmosphere = serializers.SerializerMethodField()
    dietary_options = serializers.SerializerMethodField()
    special_experiences = serializers.SerializerMethodField()
    dress_code = serializers.SerializerMethodField()
    reservation_required = serializers.SerializerMethodField()
    parking_available = serializers.SerializerMethodField()
    web_search_context = serializers.SerializerMethodField()
    web_search_sources = serializers.SerializerMethodField()
    
    class Meta(BaseContentSerializer.Meta):
        model = RestaurantSpecific
        fields = BaseContentSerializer.Meta.fields + [
            'restaurant_name',
            'cuisine_type',
            'price_range',
            'rating',
            'number_of_reviews',
            'contact_phone',
            'website',
            'opening_hours',
            # Computed fields from field_confidence
            'signature_dishes',
            'atmosphere',
            'dietary_options',
            'special_experiences',
            'dress_code',
            'reservation_required',
            'parking_available',
            'web_search_context',
            'web_search_sources',
        ]
    
    def _get_from_field_confidence(self, obj, field_name, default=None):
        """Helper to extract data from field_confidence JSON."""
        return obj.field_confidence.get(field_name, default)
    
    def get_signature_dishes(self, obj):
        return self._get_from_field_confidence(obj, 'signature_dishes', [])
    
    def get_atmosphere(self, obj):
        return self._get_from_field_confidence(obj, 'atmosphere')
    
    def get_dietary_options(self, obj):
        return self._get_from_field_confidence(obj, 'dietary_options', [])
    
    def get_special_experiences(self, obj):
        return self._get_from_field_confidence(obj, 'special_experiences', [])
    
    def get_dress_code(self, obj):
        return self._get_from_field_confidence(obj, 'dress_code')
    
    def get_reservation_required(self, obj):
        return self._get_from_field_confidence(obj, 'reservation_required')
    
    def get_parking_available(self, obj):
        return self._get_from_field_confidence(obj, 'parking_available')
    
    def get_web_search_context(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_context')
    
    def get_web_search_sources(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_sources', [])


# =============================================================================
# TOUR SERIALIZERS
# =============================================================================

class TourGeneralSerializer(BaseContentSerializer):
    """Serializer for TourGeneral (tour guides)."""
    
    class Meta(BaseContentSerializer.Meta):
        model = TourGeneral
        fields = BaseContentSerializer.Meta.fields + [
            'destination',
            'total_tours',
            'activity_types',
            'price_range_min',
            'price_range_max',
        ]


class TourSpecificSerializer(BaseContentSerializer):
    """Serializer for TourSpecific (individual tours)."""
    
    # Computed fields
    cancellation_policy = serializers.SerializerMethodField()
    min_age = serializers.SerializerMethodField()
    fitness_level = serializers.SerializerMethodField()
    what_to_bring = serializers.SerializerMethodField()
    
    class Meta(BaseContentSerializer.Meta):
        model = TourSpecific
        fields = BaseContentSerializer.Meta.fields + [
            'tour_name',
            'duration',
            'difficulty',
            'price_adult',
            'price_child',
            'price_details',
            'group_size_max',
            'activity_type',
            'included_items',
            'excluded_items',
            'meeting_point',
            # Computed fields
            'cancellation_policy',
            'min_age',
            'fitness_level',
            'what_to_bring',
        ]
    
    def _get_from_field_confidence(self, obj, field_name, default=None):
        return obj.field_confidence.get(field_name, default)
    
    def get_cancellation_policy(self, obj):
        return self._get_from_field_confidence(obj, 'cancellation_policy')
    
    def get_min_age(self, obj):
        return self._get_from_field_confidence(obj, 'min_age')
    
    def get_fitness_level(self, obj):
        return self._get_from_field_confidence(obj, 'fitness_level')
    
    def get_what_to_bring(self, obj):
        return self._get_from_field_confidence(obj, 'what_to_bring', [])


# =============================================================================
# TRANSPORTATION SERIALIZERS
# =============================================================================

class TransportationGeneralSerializer(BaseContentSerializer):
    """Serializer for TransportationGeneral (transport guides)."""
    
    class Meta(BaseContentSerializer.Meta):
        model = TransportationGeneral
        fields = BaseContentSerializer.Meta.fields + [
            'region',
            'transport_types',
            'total_routes',
        ]


class TransportationSpecificSerializer(BaseContentSerializer):
    """Serializer for TransportationSpecific (individual routes)."""
    
    # Computed fields
    schedule = serializers.SerializerMethodField()
    booking_required = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    
    class Meta(BaseContentSerializer.Meta):
        model = TransportationSpecific
        fields = BaseContentSerializer.Meta.fields + [
            'route_name',
            'departure_location',
            'arrival_location',
            'transport_type',
            'duration',
            'distance_km',
            'price_min',
            'price_max',
            'frequency',
            'operator',
            # Computed fields
            'schedule',
            'booking_required',
            'amenities',
        ]
    
    def _get_from_field_confidence(self, obj, field_name, default=None):
        return obj.field_confidence.get(field_name, default)
    
    def get_schedule(self, obj):
        return self._get_from_field_confidence(obj, 'schedule', [])
    
    def get_booking_required(self, obj):
        return self._get_from_field_confidence(obj, 'booking_required')
    
    def get_amenities(self, obj):
        return self._get_from_field_confidence(obj, 'amenities', [])


# =============================================================================
# LOCAL TIPS SERIALIZERS
# =============================================================================

class LocalTipsGeneralSerializer(BaseContentSerializer):
    """Serializer for LocalTipsGeneral (local tips guides)."""
    
    # Extract fields from field_confidence
    category = serializers.SerializerMethodField()
    practical_advice = serializers.SerializerMethodField()
    cost_estimate = serializers.SerializerMethodField()
    best_time = serializers.SerializerMethodField()
    things_to_avoid = serializers.SerializerMethodField()
    local_customs = serializers.SerializerMethodField()
    emergency_contacts = serializers.SerializerMethodField()
    web_search_context = serializers.SerializerMethodField()
    web_search_sources = serializers.SerializerMethodField()
    web_search_citations = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    page_type = serializers.SerializerMethodField()
    content_type_confidence = serializers.SerializerMethodField()
    
    # NEW: Additional structured fields
    destinations_covered = serializers.SerializerMethodField()
    budget_guide = serializers.SerializerMethodField()
    visa_info = serializers.SerializerMethodField()
    recommended_duration = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    safety_rating = serializers.SerializerMethodField()
    transportation_tips = serializers.SerializerMethodField()
    
    class Meta(BaseContentSerializer.Meta):
        model = LocalTipsGeneral
        fields = BaseContentSerializer.Meta.fields + [
            'destination',
            'tip_categories',
            # Fields from field_confidence
            'category',
            'practical_advice',
            'cost_estimate',
            'best_time',
            'things_to_avoid',
            'local_customs',
            'emergency_contacts',
            'web_search_context',
            'web_search_sources',
            'web_search_citations',
            'content_type',
            'page_type',
            'content_type_confidence',
            # NEW: Structured fields
            'destinations_covered',
            'budget_guide',
            'visa_info',
            'recommended_duration',
            'language',
            'currency',
            'safety_rating',
            'transportation_tips',
        ]
    
    def _get_from_field_confidence(self, obj, field_name, default=None):
        return obj.field_confidence.get(field_name, default)
    
    def get_category(self, obj):
        return self._get_from_field_confidence(obj, 'category')
    
    def get_practical_advice(self, obj):
        return self._get_from_field_confidence(obj, 'practical_advice')
    
    def get_cost_estimate(self, obj):
        return self._get_from_field_confidence(obj, 'cost_estimate')
    
    def get_best_time(self, obj):
        return self._get_from_field_confidence(obj, 'best_time')
    
    def get_things_to_avoid(self, obj):
        return self._get_from_field_confidence(obj, 'things_to_avoid', [])
    
    def get_local_customs(self, obj):
        return self._get_from_field_confidence(obj, 'local_customs', [])
    
    def get_emergency_contacts(self, obj):
        return self._get_from_field_confidence(obj, 'emergency_contacts', [])
    
    def get_web_search_context(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_context')
    
    def get_web_search_sources(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_sources', [])
    
    def get_web_search_citations(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_citations', [])
    
    def get_content_type(self, obj):
        return self._get_from_field_confidence(obj, 'content_type')
    
    def get_page_type(self, obj):
        return self._get_from_field_confidence(obj, 'page_type')
    
    def get_content_type_confidence(self, obj):
        return self._get_from_field_confidence(obj, 'content_type_confidence')
    
    # NEW: Getters for structured fields
    def get_destinations_covered(self, obj):
        return self._get_from_field_confidence(obj, 'destinations_covered', [])
    
    def get_budget_guide(self, obj):
        return self._get_from_field_confidence(obj, 'budget_guide')
    
    def get_visa_info(self, obj):
        return self._get_from_field_confidence(obj, 'visa_info')
    
    def get_recommended_duration(self, obj):
        return self._get_from_field_confidence(obj, 'recommended_duration')
    
    def get_language(self, obj):
        return self._get_from_field_confidence(obj, 'language')
    
    def get_currency(self, obj):
        return self._get_from_field_confidence(obj, 'currency')
    
    def get_safety_rating(self, obj):
        return self._get_from_field_confidence(obj, 'safety_rating')
    
    def get_transportation_tips(self, obj):
        return self._get_from_field_confidence(obj, 'transportation_tips')


class LocalTipsSpecificSerializer(BaseContentSerializer):
    """Serializer for LocalTipsSpecific (individual tips)."""
    
    # Extract fields from field_confidence
    practical_advice = serializers.SerializerMethodField()
    cost_estimate = serializers.SerializerMethodField()
    best_time = serializers.SerializerMethodField()
    things_to_avoid = serializers.SerializerMethodField()
    local_customs = serializers.SerializerMethodField()
    emergency_contacts = serializers.SerializerMethodField()
    
    class Meta(BaseContentSerializer.Meta):
        model = LocalTipsSpecific
        fields = BaseContentSerializer.Meta.fields + [
            'tip_title',
            'category',
            # Fields from field_confidence
            'practical_advice',
            'cost_estimate',
            'best_time',
            'things_to_avoid',
            'local_customs',
            'emergency_contacts',
        ]
    
    def _get_from_field_confidence(self, obj, field_name, default=None):
        return obj.field_confidence.get(field_name, default)
    
    def get_practical_advice(self, obj):
        return self._get_from_field_confidence(obj, 'practical_advice')
    
    def get_cost_estimate(self, obj):
        return self._get_from_field_confidence(obj, 'cost_estimate')
    
    def get_best_time(self, obj):
        return self._get_from_field_confidence(obj, 'best_time')
    
    def get_things_to_avoid(self, obj):
        return self._get_from_field_confidence(obj, 'things_to_avoid', [])
    
    def get_local_customs(self, obj):
        return self._get_from_field_confidence(obj, 'local_customs', [])
    
    def get_emergency_contacts(self, obj):
        return self._get_from_field_confidence(obj, 'emergency_contacts', [])


# =============================================================================
# CONTENT IMAGE SERIALIZER
# =============================================================================

class ContentImageSerializer(serializers.ModelSerializer):
    """Serializer for ContentImage (generic images)."""
    
    class Meta:
        model = ContentImage
        fields = [
            'id',
            'image_url',
            'caption',
            'order',
            'is_primary',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
