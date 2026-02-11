import cloudscraper
import json

scraper = cloudscraper.create_scraper()

print("Поиск API endpoint для моделей...")
print("="*80)

# Попробуем различные endpoints для моделей
endpoints = [
    'https://api2.myauto.ge/ka/getModels?man_id=1',
    'https://api2.myauto.ge/en/getModels?man_id=1',
    'https://api2.myauto.ge/ka/models?man_id=1',
    'https://api2.myauto.ge/en/models?man_id=1',
    'https://api2.myauto.ge/ka/models/1',
    'https://api2.myauto.ge/en/models/1',
]

for endpoint in endpoints:
    try:
        print(f"\nПробую: {endpoint}")
        response = scraper.get(endpoint, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  ✅ HTTP 200")
                
                if isinstance(data, dict):
                    print(f"  Ключи: {list(data.keys())}")
                    
                    # Ищем модели
                    for key in ['data', 'models', 'items']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list) and len(items) > 0:
                                print(f"  🎯 Найден массив моделей в '{key}': {len(items)} элементов")
                                print(f"  Первые 5:")
                                for item in items[:5]:
                                    print(f"    {item}")
                                
                                # Сохраняем
                                with open('models_sample.json', 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                
                                print(f"\n  ✅ Данные сохранены в models_sample.json")
                                exit(0)
                
                elif isinstance(data, list) and len(data) > 0:
                    print(f"  Прямой массив: {len(data)} элементов")
                    print(f"  Первые 5:")
                    for item in data[:5]:
                        print(f"    {item}")
                    
                    with open('models_sample.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n  ✅ Данные сохранены в models_sample.json")
                    exit(0)
                    
            except json.JSONDecodeError:
                print(f"  ❌ Не JSON")
        else:
            print(f"  HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")

print("\n" + "="*80)
print("Попробую получить модели для разных марок...")
print("="*80)

# Попробуем для разных марок
for man_id in [1, 2, 3, 41]:
    try:
        url = f'https://api2.myauto.ge/ka/getModels?man_id={man_id}'
        print(f"\nman_id={man_id}: {url}")
        response = scraper.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ {len(data)} моделей")
                print(f"  Примеры: {[m.get('model_name', m) for m in data[:3]]}")
            elif isinstance(data, dict) and 'data' in data:
                items = data['data']
                if isinstance(items, list) and len(items) > 0:
                    print(f"  ✅ {len(items)} моделей")
                    print(f"  Примеры: {[m.get('model_name', m) for m in items[:3]]}")
    except:
        pass

print("\n" + "="*80)
print("Проверка завершена")
