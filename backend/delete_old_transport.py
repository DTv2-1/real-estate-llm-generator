#!/usr/bin/env python3
"""Delete old transportation record with empty fields."""

import psycopg2

# Connect to database
conn = psycopg2.connect(
    dbname="kp_real_estate_dev",
    user="1di",
    password="",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Delete the old record with empty title
cur.execute("""
    DELETE FROM transportation_specific 
    WHERE title = '' OR title IS NULL
""")

deleted_count = cur.rowcount
conn.commit()

print(f"✅ Deleted {deleted_count} transportation record(s) with empty title")

cur.close()
conn.close()

print("\n🔄 Now you can re-extract the Rome2Rio URL to test the fixes.")
print("   The new record should have:")
print("   - title: 'San José to Manuel Antonio' (from route_name)")
print("   - route_name: 'San José to Manuel Antonio'")
print("   - departure_location: 'San José'")
print("   - arrival_location: 'Manuel Antonio National Park'")
print("   - 6 route_options in field_confidence")
