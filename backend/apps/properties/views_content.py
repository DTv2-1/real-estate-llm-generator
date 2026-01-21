"""
Views for new content type models.
Handles API endpoints for Transportation, Restaurant, Tour, etc.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models_content import (
    TransportationSpecific, TransportationGeneral,
    RestaurantSpecific, RestaurantGeneral,
    TourSpecific, TourGeneral,
    RealEstateSpecific, RealEstateGeneral,
    LocalTipsSpecific, LocalTipsGeneral,
)
from .serializers_content import (
    TransportationSpecificSerializer, TransportationGeneralSerializer,
    RestaurantSpecificSerializer, RestaurantGeneralSerializer,
    TourSpecificSerializer, TourGeneralSerializer,
    RealEstateSpecificSerializer, RealEstateGeneralSerializer,
    LocalTipsSpecificSerializer, LocalTipsGeneralSerializer,
)


class BaseContentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Base viewset for all content types.
    Provides common filtering and search functionality.
    """
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return active content for current tenant."""
        queryset = self.queryset.filter(is_active=True)
        
        # Filter by tenant if provided
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset


# =============================================================================
# TRANSPORTATION VIEWSETS
# =============================================================================

class TransportationSpecificViewSet(BaseContentViewSet):
    """
    API endpoint for specific transportation routes.
    """
    queryset = TransportationSpecific.objects.select_related('tenant').all()
    serializer_class = TransportationSpecificSerializer
    filterset_fields = ['transport_type', 'departure_location', 'arrival_location', 'operator']
    search_fields = ['title', 'route_name', 'departure_location', 'arrival_location', 'description']


class TransportationGeneralViewSet(BaseContentViewSet):
    """
    API endpoint for general transportation guides.
    """
    queryset = TransportationGeneral.objects.select_related('tenant').all()
    serializer_class = TransportationGeneralSerializer
    filterset_fields = ['region']
    search_fields = ['title', 'region', 'description']


# =============================================================================
# RESTAURANT VIEWSETS
# =============================================================================

class RestaurantSpecificViewSet(BaseContentViewSet):
    """
    API endpoint for specific restaurants.
    """
    queryset = RestaurantSpecific.objects.select_related('tenant').all()
    serializer_class = RestaurantSpecificSerializer
    filterset_fields = ['price_range']
    search_fields = ['title', 'restaurant_name', 'description', 'location']
    
    def get_queryset(self):
        """Add cuisine type filtering."""
        queryset = super().get_queryset()
        
        # Filter by cuisine (supports comma-separated list)
        cuisine = self.request.query_params.get('cuisine')
        if cuisine:
            cuisine_list = [c.strip() for c in cuisine.split(',')]
            queryset = queryset.filter(cuisine_type__overlap=cuisine_list)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        return queryset


class RestaurantGeneralViewSet(BaseContentViewSet):
    """
    API endpoint for general restaurant guides.
    """
    queryset = RestaurantGeneral.objects.select_related('tenant').all()
    serializer_class = RestaurantGeneralSerializer
    filterset_fields = ['destination']
    search_fields = ['title', 'destination', 'description']


# =============================================================================
# TOUR VIEWSETS
# =============================================================================

class TourSpecificViewSet(BaseContentViewSet):
    """
    API endpoint for specific tours/activities.
    """
    queryset = TourSpecific.objects.select_related('tenant').all()
    serializer_class = TourSpecificSerializer
    filterset_fields = ['difficulty']
    search_fields = ['title', 'tour_name', 'description', 'location']
    
    def get_queryset(self):
        """Add tour-specific filtering."""
        queryset = super().get_queryset()
        
        # Filter by activity type
        activity = self.request.query_params.get('activity')
        if activity:
            queryset = queryset.filter(activity_type__contains=[activity])
        
        # Filter by price range
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_adult__lte=float(max_price))
        
        # Filter by duration
        max_duration = self.request.query_params.get('max_duration')
        if max_duration:
            queryset = queryset.filter(duration__lte=max_duration)
        
        return queryset


class TourGeneralViewSet(BaseContentViewSet):
    """
    API endpoint for general tour guides.
    """
    queryset = TourGeneral.objects.select_related('tenant').all()
    serializer_class = TourGeneralSerializer
    filterset_fields = ['destination']
    search_fields = ['title', 'destination', 'description']


# =============================================================================
# REAL ESTATE VIEWSETS
# =============================================================================

class RealEstateSpecificViewSet(BaseContentViewSet):
    """
    API endpoint for specific real estate listings.
    """
    queryset = RealEstateSpecific.objects.select_related('tenant').all()
    serializer_class = RealEstateSpecificSerializer
    filterset_fields = ['property_type', 'status']
    search_fields = ['title', 'description', 'location']
    
    def get_queryset(self):
        """Add real estate filtering."""
        queryset = super().get_queryset()
        
        # Price filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_usd__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price_usd__lte=float(max_price))
        
        # Bedrooms/bathrooms filtering
        bedrooms = self.request.query_params.get('bedrooms')
        bathrooms = self.request.query_params.get('bathrooms')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=int(bedrooms))
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=int(bathrooms))
        
        return queryset


class RealEstateGeneralViewSet(BaseContentViewSet):
    """
    API endpoint for general real estate guides.
    """
    queryset = RealEstateGeneral.objects.select_related('tenant').all()
    serializer_class = RealEstateGeneralSerializer
    filterset_fields = ['destination']
    search_fields = ['title', 'destination', 'description']


# =============================================================================
# LOCAL TIPS VIEWSETS
# =============================================================================

class LocalTipsSpecificViewSet(BaseContentViewSet):
    """
    API endpoint for specific local tips.
    """
    queryset = LocalTipsSpecific.objects.select_related('tenant').all()
    serializer_class = LocalTipsSpecificSerializer
    filterset_fields = ['category']
    search_fields = ['title', 'tip_title', 'description']


class LocalTipsGeneralViewSet(BaseContentViewSet):
    """
    API endpoint for general local tips guides.
    """
    queryset = LocalTipsGeneral.objects.select_related('tenant').all()
    serializer_class = LocalTipsGeneralSerializer
    filterset_fields = ['destination']
    search_fields = ['title', 'destination', 'description']
