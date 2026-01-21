#!/usr/bin/env python3
"""Quick script to check if Rome2Rio data was saved."""

import os
import sys
import django
from pathlib import Path

# Setup Django
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.properties.models_content import TransportationSpecific

# Get the last saved transportation
transport = TransportationSpecific.objects.order_by('-created_at').first()

if transport:
    print('✅ FOUND TransportationSpecific record:')
    print(f'   ID: {transport.id}')
    print(f'   Title: {repr(transport.title)}')
    print(f'   Route Name: {transport.route_name}')
    print(f'   Departure: {transport.departure_location}')
    print(f'   Arrival: {transport.arrival_location}')
    print(f'   Distance: {transport.distance_km} km')
    print(f'   Source URL: {transport.source_url}')
    print(f'   Created: {transport.created_at}')
    print()
    
    # Check field_confidence for route_options
    if transport.field_confidence:
        fc = transport.field_confidence
        if 'route_options' in fc:
            route_opts = fc['route_options']
            print(f'   📊 Route Options: {len(route_opts)} options found')
            for i, opt in enumerate(route_opts, 1):
                transport_type = opt.get('transport_type', '?')
                duration = opt.get('duration_hours', '?')
                price_min = opt.get('price_min_usd', '?')
                operator = opt.get('operator', '')
                print(f'      {i}. {transport_type.upper()}: {duration}h - ${price_min}+ ({operator})')
        else:
            print('   ⚠️  No route_options in field_confidence')
            print(f'   Available keys: {list(fc.keys())}')
    else:
        print('   ⚠️  field_confidence is empty')
else:
    print('❌ No TransportationSpecific records found')
