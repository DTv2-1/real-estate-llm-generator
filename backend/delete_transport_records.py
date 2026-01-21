#!/usr/bin/env python3
"""Delete all transportation records to test fresh extraction."""

import os
import sys
import django
from pathlib import Path

# Setup Django
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Load .env
from dotenv import load_dotenv
env_file = backend_path / '.env'
if env_file.exists():
    load_dotenv(env_file, override=True)

django.setup()

from apps.properties.models_content import TransportationSpecific, TransportationGeneral

# Delete all transportation records
specific_count = TransportationSpecific.objects.all().count()
general_count = TransportationGeneral.objects.all().count()

print(f"🗑️  Deleting {specific_count} TransportationSpecific records...")
TransportationSpecific.objects.all().delete()

print(f"🗑️  Deleting {general_count} TransportationGeneral records...")
TransportationGeneral.objects.all().delete()

print("\n✅ All transportation records deleted!")
print("\n📝 Now you can test fresh extraction from Rome2Rio")
