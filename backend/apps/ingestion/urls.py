from django.urls import path
from .views import IngestURLView, IngestTextView, IngestBatchView, SavePropertyView

urlpatterns = [
    path('url/', IngestURLView.as_view(), name='ingest-url'),
    path('text/', IngestTextView.as_view(), name='ingest-text'),
    path('batch/', IngestBatchView.as_view(), name='ingest-batch'),
    path('save/', SavePropertyView.as_view(), name='save-property'),
]
