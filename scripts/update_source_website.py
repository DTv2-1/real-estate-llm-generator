#!/usr/bin/env python
"""
Script to update existing properties with source_website field based on their source_url.
Run: python manage.py shell < scripts/update_source_website.py
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.properties.models import Property
from core.utils.website_detector import detect_source_website

def update_properties():
    """Update all properties with source_website based on their source_url."""
    
    properties = Property.objects.all()
    total = properties.count()
    
    print(f"Found {total} properties to update")
    
    updated = 0
    for prop in properties:
        if prop.source_url:
            detected = detect_source_website(prop.source_url)
            if prop.source_website != detected:
                prop.source_website = detected
                prop.save(update_fields=['source_website'])
                updated += 1
                print(f"✓ Updated {prop.property_name[:50]}: {detected}")
        else:
            # Set to 'other' if no source_url
            if prop.source_website != 'other':
                prop.source_website = 'other'
                prop.save(update_fields=['source_website'])
                updated += 1
                print(f"✓ Updated {prop.property_name[:50]}: other (no URL)")
    
    print(f"\n✅ Updated {updated}/{total} properties")
    
    # Show summary
    summary = Property.objects.values('source_website').annotate(count=django.db.models.Count('id'))
    print("\n📊 Summary by website:")
    for item in summary:
        print(f"  {item['source_website']}: {item['count']}")

if __name__ == '__main__':
    update_properties()
