"""
Content models for different types: Property, Restaurant, Tour, Transportation, LocalTips.
Each type has GENERAL (guides/listings) and SPECIFIC (individual items) models.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.utils.translation import gettext_lazy as _
from pgvector.django import VectorField

from apps.tenants.models import Tenant


class SourceWebsite:
    """Source website constants."""
    ENCUENTRA24 = 'encuentra24'
    CR_REALESTATE = 'crrealestate'
    COLDWELL_BANKER = 'coldwellbanker'
    TRIPADVISOR = 'tripadvisor'
    DESAFIO = 'desafio'
    ROME2RIO = 'rome2rio'
    OTHER = 'other'
    
    CHOICES = [
        (ENCUENTRA24, _('Encuentra24')),
        (CR_REALESTATE, _('CR Real Estate')),
        (COLDWELL_BANKER, _('Coldwell Banker')),
        (TRIPADVISOR, _('TripAdvisor')),
        (DESAFIO, _('Desafio')),
        (ROME2RIO, _('Rome2Rio')),
        (OTHER, _('Other')),
    ]


# =============================================================================
# BASE ABSTRACT MODEL
# =============================================================================

class BaseContent(models.Model):
    """
    Abstract base model for all content types.
    Contains common fields shared across all content.
    """
    
    # Primary identification
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='%(class)s_items',
        verbose_name=_('Tenant')
    )
    
    # Basic information
    title = models.CharField(
        _('Title'),
        max_length=300,
        help_text=_('Title or name')
    )
    
    description = models.TextField(
        _('Description'),
        null=True,
        blank=True,
        help_text=_('Full description')
    )
    
    # Location
    location = models.CharField(
        _('Location'),
        max_length=200,
        null=True,
        blank=True,
        help_text=_('City, region, or area')
    )
    
    latitude = models.DecimalField(
        _('Latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    longitude = models.DecimalField(
        _('Longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # Metadata
    source_website = models.CharField(
        _('Source Website'),
        max_length=50,
        choices=SourceWebsite.CHOICES,
        default=SourceWebsite.OTHER
    )
    
    source_url = models.URLField(
        _('Source URL'),
        max_length=500,
        unique=True
    )
    
    raw_html = models.TextField(
        _('Raw HTML'),
        null=True,
        blank=True
    )
    
    # Extraction metadata
    extraction_confidence = models.DecimalField(
        _('Extraction Confidence'),
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    field_confidence = models.JSONField(
        _('Field Confidence & Extra Data'),
        default=dict,
        blank=True,
        help_text=_('Per-field confidence scores and content-specific extra fields')
    )
    
    extracted_at = models.DateTimeField(
        _('Extracted At'),
        auto_now_add=True
    )
    
    # User role visibility
    user_roles = ArrayField(
        models.CharField(max_length=20),
        default=list,
        blank=True,
        verbose_name=_('Visible to Roles')
    )
    
    # Status
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    
    # Vector embeddings for semantic search
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        verbose_name=_('Embedding Vector')
    )
    
    content_for_search = models.TextField(
        _('Content for Search'),
        null=True,
        blank=True,
        help_text=_('Pre-computed text content for embeddings')
    )
    
    search_vector = SearchVectorField(
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['source_website']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title


# =============================================================================
# REAL ESTATE MODELS
# =============================================================================

class RealEstateGeneral(BaseContent):
    """
    General real estate guide/listing pages.
    E.g., "Properties for sale in San Jose", market overview pages.
    """
    
    destination = models.CharField(
        _('Destination'),
        max_length=200,
        help_text=_('City or region covered')
    )
    
    total_properties = models.IntegerField(
        _('Total Properties'),
        null=True,
        blank=True
    )
    
    price_range_min = models.DecimalField(
        _('Min Price (USD)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    price_range_max = models.DecimalField(
        _('Max Price (USD)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    property_types = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_('Property Types Available')
    )
    
    popular_areas = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    
    # Overview/market info stored in field_confidence JSON:
    # - overview, market_trends, investment_tips, legal_considerations, featured_properties
    
    class Meta:
        db_table = 'real_estate_general'
        verbose_name = _('Real Estate General Guide')
        verbose_name_plural = _('Real Estate General Guides')
        ordering = ['-created_at']


class RealEstateSpecific(BaseContent):
    """
    Specific property listings.
    E.g., individual house, condo, land for sale.
    """
    
    PROPERTY_TYPES = [
        ('house', _('House')),
        ('condo', _('Condominium')),
        ('villa', _('Villa')),
        ('land', _('Land')),
        ('commercial', _('Commercial')),
        ('apartment', _('Apartment')),
    ]
    
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('pending', _('Pending')),
        ('sold', _('Sold')),
        ('off_market', _('Off Market')),
    ]
    
    property_type = models.CharField(
        _('Property Type'),
        max_length=20,
        choices=PROPERTY_TYPES
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    
    price_usd = models.DecimalField(
        _('Price (USD)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    bedrooms = models.IntegerField(
        _('Bedrooms'),
        null=True,
        blank=True
    )
    
    bathrooms = models.DecimalField(
        _('Bathrooms'),
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True
    )
    
    square_meters = models.DecimalField(
        _('Square Meters'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    lot_size_m2 = models.DecimalField(
        _('Lot Size (m²)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    amenities = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    
    year_built = models.IntegerField(
        _('Year Built'),
        null=True,
        blank=True
    )
    
    parking_spaces = models.IntegerField(
        _('Parking Spaces'),
        null=True,
        blank=True
    )
    
    hoa_fee_monthly = models.DecimalField(
        _('HOA Fee (Monthly)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    property_tax_annual = models.DecimalField(
        _('Property Tax (Annual)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    listing_id = models.CharField(
        _('Listing ID'),
        max_length=50,
        null=True,
        blank=True
    )
    
    date_listed = models.DateField(
        _('Date Listed'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'real_estate_specific'
        verbose_name = _('Real Estate Property')
        verbose_name_plural = _('Real Estate Properties')
        ordering = ['-created_at']


# =============================================================================
# RESTAURANT MODELS
# =============================================================================

class RestaurantGeneral(BaseContent):
    """
    General restaurant guides/listings.
    E.g., "Best restaurants in San Jose", restaurant district guides.
    """
    
    destination = models.CharField(
        _('Destination'),
        max_length=200
    )
    
    total_restaurants = models.IntegerField(
        _('Total Restaurants'),
        null=True,
        blank=True
    )
    
    cuisine_types = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    
    price_ranges = ArrayField(
        models.CharField(max_length=20),
        blank=True,
        default=list
    )
    
    neighborhoods = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    
    # Overview stored in field_confidence JSON
    
    class Meta:
        db_table = 'restaurant_general'
        verbose_name = _('Restaurant General Guide')
        verbose_name_plural = _('Restaurant General Guides')
        ordering = ['-created_at']


class RestaurantSpecific(BaseContent):
    """
    Specific restaurant listings.
    """
    
    restaurant_name = models.CharField(
        _('Restaurant Name'),
        max_length=200
    )
    
    cuisine_type = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    
    price_range = models.CharField(
        _('Price Range'),
        max_length=20,
        null=True,
        blank=True,
        help_text=_('$, $$, $$$, $$$$')
    )
    
    rating = models.DecimalField(
        _('Rating'),
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    number_of_reviews = models.IntegerField(
        _('Number of Reviews'),
        null=True,
        blank=True
    )
    
    contact_phone = models.CharField(
        _('Contact Phone'),
        max_length=50,
        null=True,
        blank=True
    )
    
    website = models.URLField(
        _('Website'),
        max_length=500,
        null=True,
        blank=True
    )
    
    opening_hours = models.JSONField(
        _('Opening Hours'),
        default=dict,
        blank=True
    )
    
    # Additional fields in field_confidence JSON:
    # signature_dishes, atmosphere, dietary_options, special_experiences,
    # amenities, dress_code, reservation_required, parking_available
    
    class Meta:
        db_table = 'restaurant_specific'
        verbose_name = _('Restaurant')
        verbose_name_plural = _('Restaurants')
        ordering = ['-created_at']


# =============================================================================
# TOUR MODELS
# =============================================================================

class TourGeneral(BaseContent):
    """
    General tour/activity guides.
    E.g., "Tours in Arenal", "Adventure activities in Costa Rica".
    """
    
    destination = models.CharField(
        _('Destination'),
        max_length=200
    )
    
    total_tours = models.IntegerField(
        _('Total Tours'),
        null=True,
        blank=True
    )
    
    activity_types = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    
    price_range_min = models.DecimalField(
        _('Min Price (USD)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    price_range_max = models.DecimalField(
        _('Max Price (USD)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'tour_general'
        verbose_name = _('Tour General Guide')
        verbose_name_plural = _('Tour General Guides')
        ordering = ['-created_at']


class TourSpecific(BaseContent):
    """
    Specific tour/activity listings.
    """
    
    tour_name = models.CharField(
        _('Tour Name'),
        max_length=300
    )
    
    duration = models.CharField(
        _('Duration'),
        max_length=100,
        null=True,
        blank=True
    )
    
    difficulty = models.CharField(
        _('Difficulty'),
        max_length=50,
        null=True,
        blank=True
    )
    
    price_adult = models.DecimalField(
        _('Price Adult (USD)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    price_child = models.DecimalField(
        _('Price Child (USD)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    price_details = models.JSONField(
        _('Price Details'),
        default=dict,
        blank=True
    )
    
    group_size_max = models.IntegerField(
        _('Max Group Size'),
        null=True,
        blank=True
    )
    
    activity_type = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    
    included_items = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list
    )
    
    excluded_items = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list
    )
    
    meeting_point = models.CharField(
        _('Meeting Point'),
        max_length=500,
        null=True,
        blank=True
    )
    
    # Additional fields in field_confidence JSON:
    # cancellation_policy, min_age, fitness_level, what_to_bring
    
    class Meta:
        db_table = 'tour_specific'
        verbose_name = _('Tour')
        verbose_name_plural = _('Tours')
        ordering = ['-created_at']


# =============================================================================
# TRANSPORTATION MODELS
# =============================================================================

class TransportationGeneral(BaseContent):
    """
    General transportation guides.
    E.g., "Transportation in Costa Rica", regional transport overview.
    """
    
    region = models.CharField(
        _('Region'),
        max_length=200
    )
    
    transport_types = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    
    total_routes = models.IntegerField(
        _('Total Routes'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'transportation_general'
        verbose_name = _('Transportation General Guide')
        verbose_name_plural = _('Transportation General Guides')
        ordering = ['-created_at']


class TransportationSpecific(BaseContent):
    """
    Specific transportation routes.
    """
    
    route_name = models.CharField(
        _('Route Name'),
        max_length=300
    )
    
    departure_location = models.CharField(
        _('Departure Location'),
        max_length=200
    )
    
    arrival_location = models.CharField(
        _('Arrival Location'),
        max_length=200
    )
    
    transport_type = models.CharField(
        _('Transport Type'),
        max_length=50,
        help_text=_('Bus, shuttle, taxi, car, plane, etc.')
    )
    
    duration = models.CharField(
        _('Duration'),
        max_length=100,
        null=True,
        blank=True
    )
    
    distance_km = models.DecimalField(
        _('Distance (km)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    price_min = models.DecimalField(
        _('Min Price (USD)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    price_max = models.DecimalField(
        _('Max Price (USD)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    frequency = models.CharField(
        _('Frequency'),
        max_length=200,
        null=True,
        blank=True,
        help_text=_('How often service runs')
    )
    
    operator = models.CharField(
        _('Operator'),
        max_length=200,
        null=True,
        blank=True
    )
    
    # Additional fields in field_confidence JSON:
    # schedule, booking_required, amenities
    
    class Meta:
        db_table = 'transportation_specific'
        verbose_name = _('Transportation Route')
        verbose_name_plural = _('Transportation Routes')
        ordering = ['-created_at']


# =============================================================================
# LOCAL TIPS MODELS
# =============================================================================

class LocalTipsGeneral(BaseContent):
    """
    General local tips/guides.
    E.g., "Costa Rica travel guide", "What to know before visiting".
    
    Additional structured fields for destinations, budget, visa, language stored in field_confidence JSON:
    - destinations_covered: Array of destination objects with highlights
    - budget_guide: Object with budget/mid_range/luxury ranges
    - visa_info: String with visa requirements
    - recommended_duration: String with suggested trip length
    - language: String with language info
    - currency: String with currency info
    - safety_rating: String with safety level
    - transportation_tips: String with getting around advice
    """
    
    destination = models.CharField(
        _('Destination'),
        max_length=200
    )
    
    tip_categories = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    
    class Meta:
        db_table = 'local_tips_general'
        verbose_name = _('Local Tips General Guide')
        verbose_name_plural = _('Local Tips General Guides')
        ordering = ['-created_at']


class LocalTipsSpecific(BaseContent):
    """
    Specific local tips/advice.
    """
    
    tip_title = models.CharField(
        _('Tip Title'),
        max_length=300
    )
    
    category = models.CharField(
        _('Category'),
        max_length=100,
        null=True,
        blank=True
    )
    
    # Content in description and field_confidence JSON
    
    class Meta:
        db_table = 'local_tips_specific'
        verbose_name = _('Local Tip')
        verbose_name_plural = _('Local Tips')
        ordering = ['-created_at']


# =============================================================================
# PROPERTY IMAGES (can be used across content types)
# =============================================================================

class ContentImage(models.Model):
    """
    Images for any content type using GenericForeignKey.
    """
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    image_url = models.URLField(
        _('Image URL'),
        max_length=500
    )
    
    caption = models.CharField(
        _('Caption'),
        max_length=500,
        null=True,
        blank=True
    )
    
    order = models.IntegerField(
        _('Order'),
        default=0
    )
    
    is_primary = models.BooleanField(
        _('Is Primary'),
        default=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_images'
        ordering = ['order', '-is_primary', 'created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Image for {self.content_object}"
