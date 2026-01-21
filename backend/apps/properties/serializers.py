"""
Serializers for Properties app.
"""

from rest_framework import serializers
from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for property images."""
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'caption', 'order', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for property lists."""
    
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_website_display = serializers.CharField(source='get_source_website_display', read_only=True)
    primary_image = serializers.SerializerMethodField()
    has_embedding = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'property_name', 'property_type', 'property_type_display',
            'price_usd', 'bedrooms', 'bathrooms', 'square_meters',
            'location', 'latitude', 'longitude', 'status', 'status_display', 
            'source_website', 'source_website_display', 'source_url', 
            'listing_id', 'listing_status', 'primary_image', 'description',
            'has_embedding', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image URL."""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return primary.image_url
        first = obj.images.first()
        return first.image_url if first else None
    
    def get_has_embedding(self, obj):
        """Check if property has embedding."""
        return obj.embedding is not None


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for property detail view."""
    
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_website_display = serializers.CharField(source='get_source_website_display', read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    price_per_sqm = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='get_price_per_sqm')
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True, allow_null=True)
    
    # Add content-specific fields from field_confidence JSON
    restaurant_name = serializers.SerializerMethodField()
    cuisine_type = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    number_of_reviews = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    opening_hours = serializers.SerializerMethodField()
    signature_dishes = serializers.SerializerMethodField()
    atmosphere = serializers.SerializerMethodField()
    dietary_options = serializers.SerializerMethodField()
    special_experiences = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    web_search_context = serializers.SerializerMethodField()
    web_search_sources = serializers.SerializerMethodField()
    web_search_citations = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'tenant', 'property_name', 'property_type', 'property_type_display',
            'price_usd', 'price_details', 'bedrooms', 'bathrooms', 'square_meters', 'lot_size_m2',
            'location', 'latitude', 'longitude', 'description', 'amenities',
            'hoa_fee_monthly', 'property_tax_annual', 'year_built', 'parking_spaces',
            'status', 'status_display', 'user_roles', 'source_website', 
            'source_website_display', 'source_url',
            'listing_id', 'internal_property_id', 'listing_status', 'date_listed',
            'extraction_confidence', 'content_type', 'page_type', 'field_confidence', 'extracted_at',
            'last_verified', 'verified_by_name', 'is_active',
            'images', 'price_per_sqm', 'created_at', 'updated_at',
            # Content-specific fields
            'restaurant_name', 'cuisine_type', 'price_range', 'rating', 'number_of_reviews',
            'contact_phone', 'opening_hours', 'signature_dishes', 'atmosphere',
            'dietary_options', 'special_experiences', 'contact_details',
            'web_search_context', 'web_search_sources', 'web_search_citations'
        ]
        read_only_fields = ['id', 'tenant', 'extracted_at', 'created_at', 'updated_at']
    
    def _get_from_field_confidence(self, obj, field_name):
        """Helper to get field from field_confidence JSON."""
        if obj.field_confidence and isinstance(obj.field_confidence, dict):
            return obj.field_confidence.get(field_name)
        return None
    
    def get_restaurant_name(self, obj):
        return self._get_from_field_confidence(obj, 'restaurant_name')
    
    def get_cuisine_type(self, obj):
        return self._get_from_field_confidence(obj, 'cuisine_type')
    
    def get_price_range(self, obj):
        return self._get_from_field_confidence(obj, 'price_range')
    
    def get_rating(self, obj):
        return self._get_from_field_confidence(obj, 'rating')
    
    def get_number_of_reviews(self, obj):
        return self._get_from_field_confidence(obj, 'number_of_reviews')
    
    def get_contact_phone(self, obj):
        return self._get_from_field_confidence(obj, 'contact_phone')
    
    def get_opening_hours(self, obj):
        return self._get_from_field_confidence(obj, 'opening_hours')
    
    def get_signature_dishes(self, obj):
        return self._get_from_field_confidence(obj, 'signature_dishes')
    
    def get_atmosphere(self, obj):
        return self._get_from_field_confidence(obj, 'atmosphere')
    
    def get_dietary_options(self, obj):
        return self._get_from_field_confidence(obj, 'dietary_options')
    
    def get_special_experiences(self, obj):
        return self._get_from_field_confidence(obj, 'special_experiences')
    
    def get_contact_details(self, obj):
        return self._get_from_field_confidence(obj, 'contact_details')
    
    def get_web_search_context(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_context')
    
    def get_web_search_sources(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_sources')
    
    def get_web_search_citations(self, obj):
        return self._get_from_field_confidence(obj, 'web_search_citations')


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating properties."""
    
    class Meta:
        model = Property
        fields = [
            'property_name', 'property_type', 'price_usd', 'bedrooms', 'bathrooms',
            'square_meters', 'lot_size_m2', 'location', 'latitude', 'longitude',
            'description', 'amenities', 'hoa_fee_monthly', 'property_tax_annual',
            'year_built', 'parking_spaces', 'status', 'user_roles', 'source_website',
            'source_url', 'listing_id', 'internal_property_id', 'listing_status', 
            'date_listed', 'raw_html', 'extraction_confidence', 'field_confidence'
        ]
    
    def validate_price_usd(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        if data.get('square_meters') and data['square_meters'] <= 0:
            raise serializers.ValidationError({"square_meters": "Must be greater than 0"})
        
        if data.get('bedrooms') and data['bedrooms'] < 0:
            raise serializers.ValidationError({"bedrooms": "Cannot be negative"})
        
        if data.get('bathrooms') and data['bathrooms'] < 0:
            raise serializers.ValidationError({"bathrooms": "Cannot be negative"})
        
        return data


class PropertyVerifySerializer(serializers.Serializer):
    """Serializer for verifying properties."""
    
    verified = serializers.BooleanField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)
