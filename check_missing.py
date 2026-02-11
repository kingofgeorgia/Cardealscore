import json

with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Недостающие
missing = [1, 12, 14, 16, 30, 31, 33, 41, 42, 53]

for man_id in missing:
    print(f"\n{'='*60}")
    print(f"man_id={man_id}")
    print('='*60)
    
    samples = [c for c in cars if c['make'] == man_id][:5]
    
    for car in samples:
        print(f"${car['price_usd']:>6} | {car['year']} | {car['engine_volume']:>4}cc | model: {car['model'][:50]}")
