#!/usr/bin/env python
"""Analyze API response structure."""

import cloudscraper
from fake_useragent import UserAgent
import json

scraper = cloudscraper.create_scraper()
ua = UserAgent()

scraper.headers.update({
    'User-Agent': ua.random,
    'Accept': 'application/json',
})

try:
    response = scraper.get(
        "https://api2.myauto.ge/en/products",
        params={
            'vehicleType': 0,
            'Page': 1,
        },
        timeout=15
    )
    
    data = response.json()
    
    # Print top-level keys
    if isinstance(data, dict):
        print("Top-level keys:")
        for key in data.keys():
            print(f"  - {key}")
            
        # Check for listing data in various places
        if 'data' in data:
            print(f"\ndata type: {type(data['data'])}")
            if isinstance(data['data'], (list, dict)):
                if isinstance(data['data'], list) and data['data']:
                    print(f"  First item keys: {data['data'][0].keys() if isinstance(data['data'][0], dict) else 'not a dict'}")
                elif isinstance(data['data'], dict):
                    print(f"  data keys: {data['data'].keys()}")
                    
        if 'cars' in data:
            print(f"\ncars type: {type(data['cars'])}")
            
        if 'listings' in data:
            print(f"\nlistings type: {type(data['listings'])}")
            
        # Save full response for inspection
        with open('api_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\n✓ Полный ответ сохранен в api_response.json")
        
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
