import psycopg2
import json

# Connect to database (using LOCAL_DB credentials from .env)
conn = psycopg2.connect(
    dbname="kp_real_estate_dev",
    user="1di",
    password="",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Check TransportationSpecific table
cur.execute("""
    SELECT id, title, route_name, departure_location, arrival_location, 
           distance_km, source_url, field_confidence, created_at
    FROM transportation_specific 
    ORDER BY created_at DESC 
    LIMIT 1
""")

result = cur.fetchone()

if result:
    print('✅ FOUND TransportationSpecific record:')
    print(f'   ID: {result[0]}')
    print(f'   Title: {repr(result[1])}')
    print(f'   Route Name: {result[2]}')
    print(f'   Departure: {result[3]}')
    print(f'   Arrival: {result[4]}')
    print(f'   Distance: {result[5]} km')
    print(f'   Source URL: {result[6]}')
    print(f'   Created: {result[8]}')
    print()
    
    # Check field_confidence
    field_conf = result[7]
    if field_conf:
        if 'route_options' in field_conf:
            route_opts = field_conf['route_options']
            print(f'   📊 Route Options: {len(route_opts)} options found')
            for i, opt in enumerate(route_opts, 1):
                transport_type = opt.get('transport_type', '?')
                duration = opt.get('duration_hours', '?')
                price_min = opt.get('price_min_usd', '?')
                operator = opt.get('operator', '')
                print(f'      {i}. {transport_type.upper()}: {duration}h - ${price_min}+ ({operator})')
        else:
            print('   ⚠️  No route_options in field_confidence')
            print(f'   Available keys: {list(field_conf.keys())[:10]}')
    else:
        print('   ⚠️  field_confidence is empty')
else:
    print('❌ No TransportationSpecific records found')

cur.close()
conn.close()
