from django.urls import path
from .views import IngestURLView, IngestTextView, IngestBatchView, SavePropertyView
from .views_apify_webhook import apify_webhook
from .views_apify_sync import sync_apify_dataset

urlpatterns = [
    path('url/', IngestURLView.as_view(), name='ingest-url'),
    path('text/', IngestTextView.as_view(), name='ingest-text'),
    path('batch/', IngestBatchView.as_view(), name='ingest-batch'),
    path('save/', SavePropertyView.as_view(), name='save-property'),
    path('webhooks/apify/', apify_webhook, name='apify-webhook'),
    path('apify/sync/', sync_apify_dataset, name='apify-sync'),
]
