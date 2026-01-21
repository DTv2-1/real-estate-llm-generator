#!/usr/bin/env python3
"""Test script to verify API endpoints work."""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 TESTING CONTENT API ENDPOINTS")
print("=" * 80)

# Test 1: Transportation endpoint
print("\n📍 TEST 1: GET /content/transportation/")
response = requests.get(f"{BASE_URL}/content/transportation/")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Count: {data.get('count', 0)}")
    
    if data.get('results'):
        first = data['results'][0]
        print(f"   First record:")
        print(f"      ID: {first.get('id')}")
        print(f"      Title: {first.get('title')}")
        print(f"      Route Name: {first.get('route_name')}")
        print(f"      Departure: {first.get('departure_location')}")
        print(f"      Arrival: {first.get('arrival_location')}")
        print(f"      Distance: {first.get('distance_km')} km")
        
        # Check field_confidence for route_options
        if first.get('field_confidence'):
            fc = first['field_confidence']
            if 'route_options' in fc:
                print(f"      Route Options: {len(fc['route_options'])} found")
            else:
                print(f"      ⚠️  No route_options in field_confidence")
else:
    print(f"   ❌ Error: {response.text[:200]}")

# Test 2: Get specific transportation by ID
print("\n📍 TEST 2: GET /content/transportation/{id}/")
if response.status_code == 200 and data.get('results'):
    transport_id = data['results'][0]['id']
    detail_response = requests.get(f"{BASE_URL}/content/transportation/{transport_id}/")
    print(f"   Status: {detail_response.status_code}")
    
    if detail_response.status_code == 200:
        detail = detail_response.json()
        print(f"   ✅ Retrieved: {detail.get('title')}")
        print(f"   Route: {detail.get('departure_location')} → {detail.get('arrival_location')}")
    else:
        print(f"   ❌ Error: {detail_response.text[:200]}")

# Test 3: Restaurants endpoint
print("\n📍 TEST 3: GET /content/restaurants/")
response = requests.get(f"{BASE_URL}/content/restaurants/")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Count: {data.get('count', 0)}")
else:
    print(f"   ❌ Error: {response.text[:200]}")

# Test 4: Tours endpoint
print("\n📍 TEST 4: GET /content/tours/")
response = requests.get(f"{BASE_URL}/content/tours/")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Count: {data.get('count', 0)}")
else:
    print(f"   ❌ Error: {response.text[:200]}")

print("\n" + "=" * 80)
print("✅ API ENDPOINT TESTS COMPLETE")
print("=" * 80)
