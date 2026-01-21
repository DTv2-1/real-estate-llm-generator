"""
URL routing for new content type APIs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_content import (
    TransportationSpecificViewSet, TransportationGeneralViewSet,
    RestaurantSpecificViewSet, RestaurantGeneralViewSet,
    TourSpecificViewSet, TourGeneralViewSet,
    RealEstateSpecificViewSet, RealEstateGeneralViewSet,
    LocalTipsSpecificViewSet, LocalTipsGeneralViewSet,
)

router = DefaultRouter()

# Transportation
router.register(r'transportation', TransportationSpecificViewSet, basename='transportation')
router.register(r'transportation-guides', TransportationGeneralViewSet, basename='transportation-general')

# Restaurants
router.register(r'restaurants', RestaurantSpecificViewSet, basename='restaurant')
router.register(r'restaurant-guides', RestaurantGeneralViewSet, basename='restaurant-general')

# Tours
router.register(r'tours', TourSpecificViewSet, basename='tour')
router.register(r'tour-guides', TourGeneralViewSet, basename='tour-general')

# Real Estate
router.register(r'real-estate', RealEstateSpecificViewSet, basename='real-estate')
router.register(r'real-estate-guides', RealEstateGeneralViewSet, basename='real-estate-general')

# Local Tips
router.register(r'local-tips', LocalTipsSpecificViewSet, basename='local-tips')
router.register(r'local-tips-guides', LocalTipsGeneralViewSet, basename='local-tips-general')

urlpatterns = [
    path('', include(router.urls)),
]
