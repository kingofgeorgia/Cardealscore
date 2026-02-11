import cloudscraper
import json

scraper = cloudscraper.create_scraper()

# Уникальные man_id из наших данных
man_ids = [1, 2, 3, 5, 7, 10, 11, 12, 14, 16, 18, 19, 20, 22, 23, 24, 25, 28, 29, 30, 31, 33, 34, 38, 39, 41, 42, 43, 53, 61, 75, 89, 110, 124, 155, 161, 394, 786, 987]

result = {}

print("Получаем примеры автомобилей для каждого man_id...")
print("="*80)

for man_id in man_ids:
    try:
        url = 'https://api2.myauto.ge/ka/products/'
        params = {
            'TypeID': 0,
            'MakeID': man_id,
            'PerPage': 1,
        }
        
        response = scraper.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'items' in data['data']:
                items = data['data']['items']
                if len(items) > 0:
                    item = items[0]
                    car_id = item.get('car_id')
                    model = item.get('car_model', 'N/A')[:40]
                    year = item.get('prod_year')
                    engine = item.get('engine_volume')
                    price = item.get('price_usd')
                    
                    result[man_id] = {
                        'car_id': car_id,
                        'model': model,
                        'year': year,
                        'engine': engine,
                        'price': price
                    }
                    
                    print(f"man_id={man_id:3} | год={year} | объем={engine:4} | цена=${price:6} | модель={model}")
    except Exception as e:
        print(f"man_id={man_id:3} | ОШИБКА: {e}")

print("\n" + "="*80)
print(f"Всего получено данных для {len(result)} марок из {len(man_ids)}")

# Попробуем определить марки по характерных моделях
print("\n" + "="*80)
print("ОПРЕДЕЛЕНИЕ МАРОК ПО МОДЕЛЯМ:")
print("="*80)

brand_patterns = {
    'xDrive': 'BMW',
    'quattro': 'Audi',
    'Premium Plus': 'Audi',
    'LT Auto': 'Chevrolet',
    'SRT': 'Dodge',
    'Rubicon': 'Jeep',
    'Wrangler': 'Jeep',
    'F sport': 'Lexus',
    'R-Dynamic': 'Land Rover',
    'Range Rover': 'Land Rover',
    'S-ALL4': 'MINI',
    'SPORTERO': 'Mitsubishi',
    'All-wheel Drive': 'Subaru',  # характерно для Subaru
    'LONG RANGE': 'Tesla',
    'DUAL MOTOR': 'Tesla',
}

guessed_brands = {}
for man_id, info in result.items():
    model = info['model']
    guessed = None
    for pattern, brand in brand_patterns.items():
        if pattern.lower() in model.lower():
            guessed = brand
            break
    
    if guessed:
        guessed_brands[man_id] = guessed
        print(f"man_id={man_id:3} → {guessed:15} (модель: {model})")

print("\n" + "="*80)
print(f"Определено {len(guessed_brands)} марок из {len(result)}")

# Сохраним результаты
with open('detected_makes.json', 'w', encoding='utf-8') as f:
    json.dump({
        'raw_data': result,
        'guessed_brands': guessed_brands
    }, f, ensure_ascii=False, indent=2)

print("\nДанные сохранены в detected_makes.json")
