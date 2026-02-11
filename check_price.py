#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('mileon_saas.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT price_usd FROM car_listings WHERE source_listing_id = '120369874'
""")

row = cursor.fetchone()
if row:
    print(f"Price in DB: ${row[0]}")
else:
    print("Listing not found in database")

conn.close()
