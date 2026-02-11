#!/usr/bin/env python
import json

data = json.load(open('cars_data.json', encoding='utf-8'))

# Test car 120369874
target_car = [x for x in data if x.get('car_id') == 120369874]
if target_car:
    print(f"Car 120369874: price_usd = {target_car[0].get('price_usd')}")

# Find all cars with 50000 price
items_50000 = [x for x in data if x.get('price_usd') == 50000]
print(f"\nFound {len(items_50000)} items with price 50000")
for x in items_50000[:3]:
    print(f"  car_id: {x['car_id']}, price: {x.get('price_usd')}")
