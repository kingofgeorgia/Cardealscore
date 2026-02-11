#!/usr/bin/env python
import httpx
import json

try:
    r = httpx.get('http://127.0.0.1:8000/api/listings?company_id=1&with_scores=true', timeout=10)
    data = r.json()
    item = [x for x in data if x['listing']['source_listing_id'] == '120369874']
    
    if item:
        listing = item[0]['listing']
        scores = item[0]['scores']
        print(f"Source Price (price_usd): ${listing.get('price_usd')}")
        print(f"Expected Sell Price (from scores): ${scores.get('expected_sell_price')}")
        print(f"Display Price (from scores): ${scores.get('display_price')}")
    else:
        print("Car not found in API response")
except Exception as e:
    print(f"Error: {e}")
