"""
Base utilities and shared functions for ingestion views.
"""

import logging
import uuid
from decimal import Decimal
from datetime import datetime, date

logger = logging.getLogger(__name__)


def serialize_for_json(obj):
    """Convert non-JSON-serializable objects to JSON-serializable types."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    return obj
