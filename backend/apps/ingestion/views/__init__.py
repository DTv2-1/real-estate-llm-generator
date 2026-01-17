"""
Ingestion Views Package.
Organized by functionality for better maintainability.
"""

from .basic_ingestion import (
    IngestURLView,
    IngestTextView,
    SavePropertyView,
)

from .google_sheets_auto_tabs import ProcessGoogleSheetView

from .batch_processing import (
    IngestBatchView,
    BatchExportToSheetsView,
    BatchExportToDatabaseView,
)

from .utility_views import (
    SupportedWebsitesView,
    ContentTypesView,
    IngestionStatsView,
    GenerateEmbeddingsView,
    CreateGoogleSheetTemplateView,
    CancelBatchView,
)

__all__ = [
    # Basic ingestion
    'IngestURLView',
    'IngestTextView',
    'SavePropertyView',
    
    # Google Sheets with auto-tabs
    'ProcessGoogleSheetView',
    
    # Batch processing
    'IngestBatchView',
    'BatchExportToSheetsView',
    'BatchExportToDatabaseView',
    
    # Utilities
    'SupportedWebsitesView',
    'ContentTypesView',
    'IngestionStatsView',
    'GenerateEmbeddingsView',
    'CreateGoogleSheetTemplateView',
    'CancelBatchView',
]
