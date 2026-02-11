import cloudscraper
import json

scraper = cloudscraper.create_scraper()

print("Поиск endpoint для марок автомобилей...")
print("="*80)

# Более специфичные endpoints для марок
endpoints = [
    'https://api2.myauto.ge/ka/mans',
    'https://api2.myauto.ge/en/mans',
    'https://api2.myauto.ge/ka/mans/get',
    'https://api2.myauto.ge/en/mans/get',
    'https://api2.myauto.ge/ka/filters/mans',
    'https://api2.myauto.ge/en/filters/mans',
    'https://api2.myauto.ge/ka/static/mans',
    'https://api2.myauto.ge/en/static/mans',
]

for endpoint in endpoints:
    try:
        print(f"\nПробую: {endpoint}")
        response = scraper.get(endpoint, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  ✅ HTTP 200, получен JSON")
                
                # Смотрим структуру
                if isinstance(data, dict):
                    print(f"  Ключи: {list(data.keys())}")
                    
                    # Проверяем на наличие марок
                    for key in data.keys():
                        value = data[key]
                        if isinstance(value, list) and len(value) > 0:
                            first = value[0]
                            print(f"  Массив '{key}': {len(value)} элементов")
                            print(f"  Первый элемент: {first}")
                            
                            # Проверяем, похоже ли на марки
                            if isinstance(first, dict):
                                if any(k in first for k in ['man_id', 'manufacturer_id', 'id', 'name', 'title']):
                                    print(f"  🎯 ПОХОЖЕ НА МАРКИ!")
                                    
                                    # Сохраняем
                                    with open('manufacturers_found.json', 'w', encoding='utf-8') as f:
                                        json.dump(data, f, ensure_ascii=False, indent=2)
                                    
                                    # Строим маппинг
                                    make_names = {}
                                    for item in value:
                                        man_id = item.get('man_id') or item.get('id') or item.get('manufacturer_id')
                                        name = item.get('name') or item.get('title') or item.get('man_name')
                                        
                                        if man_id is not None and name:
                                            make_names[int(man_id)] = name
                                    
                                    print(f"\n  Построен маппинг: {len(make_names)} марок")
                                    print(f"\n  Первые 20 марок:")
                                    for mid in sorted(make_names.keys())[:20]:
                                        print(f"    {mid:3}: {make_names[mid]}")
                                    
                                    # Сохраняем
                                    with open('make_names_from_api.json', 'w', encoding='utf-8') as f:
                                        json.dump(make_names, f, ensure_ascii=False, indent=2)
                                    
                                    print(f"\n{'='*80}")
                                    print("✅ ГОТОВО! Маппинг сохранен в make_names_from_api.json")
                                    print(f"{'='*80}")
                                    exit(0)
                
                elif isinstance(data, list) and len(data) > 0:
                    print(f"  Прямой массив: {len(data)} элементов")
                    print(f"  Первый: {data[0]}")
                    
            except json.JSONDecodeError:
                print(f"  ❌ Не JSON")
        else:
            print(f"  HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")

print("\n" + "="*80)
print("Попробую через параметры запроса к /products")
print("="*80)

# Иногда данные о марках можно получить через фильтры поиска
try:
    # Запрос без фильтров может вернуть доступные фильтры
    response = scraper.get('https://api2.myauto.ge/ka/products', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print("\nСтруктура ответа /products:")
        print(f"Ключи: {list(data.keys()) if isinstance(data, dict) else 'list'}")
        
        # Иногда в meta данных есть доступные фильтры
        if isinstance(data, dict):
            for key in ['filters', 'meta', 'facets', 'aggregations']:
                if key in data:
                    print(f"\n  Найден ключ '{key}':")
                    print(f"  {data[key]}")
except Exception as e:
    print(f"Ошибка: {e}")

print("\n" + "="*80)
print("ИТОГ: Автоматический поиск не дал результата")
print("Использую существующий правильный маппинг")
print("="*80)
