import cloudscraper
import json

scraper = cloudscraper.create_scraper()

print("Поиск API endpoint для получения списка марок...")
print("="*80)

# Попробуем различные endpoints
endpoints = [
    'https://api2.myauto.ge/ka/getManufacturers',
    'https://api2.myauto.ge/en/getManufacturers',
    'https://api2.myauto.ge/ka/manufacturers',
    'https://api2.myauto.ge/en/manufacturers',
    'https://api2.myauto.ge/ka/getProdManufacturers',
    'https://api2.myauto.ge/en/getProdManufacturers',
    'https://api2.myauto.ge/ka/cats/get',
    'https://api2.myauto.ge/en/cats/get',
]

for endpoint in endpoints:
    try:
        print(f"\nПробую: {endpoint}")
        response = scraper.get(endpoint, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Проверяем различные структуры данных
                if isinstance(data, dict):
                    print(f"  Тип: dict, ключи: {list(data.keys())}")
                    
                    # Ищем массив марок
                    for key in ['data', 'manufacturers', 'mans', 'items']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list) and len(items) > 0:
                                print(f"  ✅ НАЙДЕН массив в '{key}': {len(items)} элементов")
                                print(f"  Структура первого элемента: {items[0]}")
                                
                                # Сохраняем и прерываем поиск
                                with open('manufacturers_raw.json', 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                
                                print(f"\n{'='*80}")
                                print(f"✅ УСПЕХ! Данные сохранены в manufacturers_raw.json")
                                print(f"{'='*80}")
                                
                                # Строим маппинг
                                make_names = {}
                                for item in items:
                                    # Различные варианты структуры
                                    man_id = item.get('man_id') or item.get('id') or item.get('manufacturer_id')
                                    name = item.get('name') or item.get('man_name') or item.get('title')
                                    
                                    if man_id and name:
                                        make_names[int(man_id)] = name
                                
                                if make_names:
                                    print(f"\nПолучено {len(make_names)} марок:")
                                    for mid in sorted(make_names.keys())[:20]:
                                        print(f"  {mid:3}: {make_names[mid]}")
                                    
                                    # Сохраняем словарь
                                    with open('make_names_official.json', 'w', encoding='utf-8') as f:
                                        json.dump(make_names, f, ensure_ascii=False, indent=2)
                                    
                                    print(f"\n✅ Маппинг сохранен в make_names_official.json")
                                    
                                    # Генерируем Python код
                                    print(f"\n{'='*80}")
                                    print("Python код для parser.py:")
                                    print('='*80)
                                    print("\nMAKE_NAMES = {")
                                    for mid in sorted(make_names.keys()):
                                        print(f"    {mid}: '{make_names[mid]}',")
                                    print("}")
                                
                                exit(0)
                            elif isinstance(items, dict):
                                print(f"  Найден dict в '{key}': {len(items)} элементов")
                                print(f"  Первый ключ/значение: {list(items.items())[0] if items else 'пусто'}")
                
                elif isinstance(data, list):
                    print(f"  Тип: list, элементов: {len(data)}")
                    if len(data) > 0:
                        print(f"  Первый элемент: {data[0]}")
            except json.JSONDecodeError:
                print(f"  ❌ Не JSON ответ")
        else:
            print(f"  HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")

print("\n" + "="*80)
print("❌ Не удалось найти API endpoint с марками")
print("Попробую альтернативный метод - анализ JavaScript файлов сайта")
print("="*80)

# Альтернатива: загрузить главную страницу и найти JS файлы
try:
    print("\nЗагружаю главную страницу...")
    response = scraper.get('https://www.myauto.ge', timeout=15)
    html = response.text
    
    import re
    
    # Ищем подключаемые JS файлы
    js_files = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
    
    print(f"Найдено {len(js_files)} JS файлов")
    
    for js_url in js_files[:5]:  # Проверяем первые 5
        if not js_url.startswith('http'):
            js_url = 'https://www.myauto.ge' + js_url
        
        print(f"\nПроверяю: {js_url}")
        
        try:
            js_response = scraper.get(js_url, timeout=5)
            js_content = js_response.text
            
            # Ищем упоминания справочника марок
            if 'manufacturer' in js_content.lower() or 'man_id' in js_content.lower():
                print(f"  ✅ Найдены упоминания марок!")
                
                # Ищем массивы с данными
                arrays = re.findall(r'(\w+)\s*=\s*(\[[\s\S]{0,1000}?\{[^\}]*man_id[^\}]*\}[\s\S]{0,500}?\])', js_content)
                if arrays:
                    print(f"  Найдено {len(arrays)} подходящих массивов")
                    # Можно попробовать распарсить, но это сложно
        except:
            pass

except Exception as e:
    print(f"Ошибка при анализе HTML: {e}")

print("\n" + "="*80)
print("РЕКОМЕНДАЦИЯ:")
print("Используйте существующий правильный маппинг из correct_make_names.py")
print("Он был построен на основе анализа реальных данных API")
print("="*80)
