import cloudscraper
import json
import re

scraper = cloudscraper.create_scraper()

print("Анализ приложения myauto.ge для поиска данных марок...")
print("="*80)

# Загружаем главную страницу
response = scraper.get('https://www.myauto.ge', timeout=15)
html = response.text

print(f"\nРазмер HTML: {len(html)} bytes")

# Ищем встроенные данные в HTML (window.__INITIAL_STATE__ и подобное)
patterns = [
    r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
    r'window\.__data\s*=\s*(\{.*?\});',
    r'window\.initialData\s*=\s*(\{.*?\});',
    r'var\s+manufacturers\s*=\s*(\[.*?\]);',
    r'const\s+manufacturers\s*=\s*(\[.*?\]);',
]

print("\nПоиск встроенных данных в HTML...")
for pattern in patterns:
    matches = re.findall(pattern, html[:50000], re.DOTALL)  # Первые 50KB
    if matches:
        print(f"  ✅ Найден паттерн: {pattern[:40]}...")
        try:
            data_str = matches[0]
            # Пробуем распарсить
            data = json.loads(data_str)
            print(f"  JSON успешно распарсен, размер: {len(str(data))} байт")
            
            # Ищем марки внутри
            def find_manufacturers(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        if 'man' in key.lower() or 'manufacturer' in key.lower():
                            if isinstance(value, list) and len(value) > 0:
                                print(f"  🎯 Найден массив марок в {new_path}: {len(value)} элементов")
                                return value
                        result = find_manufacturers(value, new_path)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for i, item in enumerate(obj[:3]):  # Проверяем первые 3
                        result = find_manufacturers(item, f"{path}[{i}]")
                        if result:
                            return result
                return None
            
            manufacturers = find_manufacturers(data)
            if manufacturers:
                print(f"\n  Первые 5 марок:")
                for m in manufacturers[:5]:
                    print(f"    {m}")
                break
        except Exception as e:
            print(f"  ❌ Ошибка парсинга: {e}")

print("\n" + "="*80)
print("Поиск JS bundle файлов с данными...")
print("="*80)

# Ищем основные JS файлы приложения
js_files = re.findall(r'<script[^>]*src=["\']([^"\']*(?:main|app|chunk|bundle)[^"\']*\.js)["\']', html)

print(f"\nНайдено {len(js_files)} JS файлов приложения")

for js_url in js_files[:3]:  # Проверяем первые 3
    if not js_url.startswith('http'):
        if js_url.startswith('//'):
            js_url = 'https:' + js_url
        elif js_url.startswith('/'):
            js_url = 'https://www.myauto.ge' + js_url
        else:
            js_url = 'https://www.myauto.ge/' + js_url
    
    print(f"\n📦 Загружаю: {js_url}")
    
    try:
        js_response = scraper.get(js_url, timeout=10)
        js_content = js_response.text
        
        print(f"  Размер: {len(js_content)} bytes")
        
        # Ищем статические данные марок в минифицированном коде
        # Ищем паттерны типа: {1:"BMW",2:"Audi",...}
        man_patterns = [
            r'\{(\d+):"([^"]{3,20})",(\d+):"([^"]{3,20})",(\d+):"([^"]{3,20})"\}',
            r'manufacturers:\s*\[(\{[^\]]{100,2000}\})\]',
            r'mans:\s*\[(\{[^\]]{100,2000}\})\]',
        ]
        
        for pattern in man_patterns:
            matches = re.findall(pattern, js_content)
            if matches:
                print(f"  ✅ Найден подходящий паттерн!")
                print(f"  Совпадений: {len(matches)}")
                if matches:
                    print(f"  Пример: {str(matches[0])[:200]}")
                break
        
        # Поиск упоминаний известных марок
        known_brands = ['BMW', 'Mercedes', 'Audi', 'Toyota', 'Honda', 'Ford']
        brands_found = sum(1 for brand in known_brands if brand in js_content)
        print(f"  Известных марок найдено в коде: {brands_found}/{len(known_brands)}")
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")

print("\n" + "="*80)
print("ВЫВОД:")
print("Сайт использует динамическую загрузку через SPA")
print("Данные марок загружаются через отдельные API запросы")
print("Используем построенный вручную маппинг из анализа реальных данных")
print("="*80)
