import cloudscraper
import re
import json

scraper = cloudscraper.create_scraper()

print("Попытка 1: Загрузка HTML страницы...")
url = 'https://www.myauto.ge'
response = scraper.get(url, timeout=10)
html = response.text

# Сохраним HTML для анализа
with open('myauto_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML сохранен в myauto_page.html ({len(html)} символов)")

# Ищем упоминания марок BMW, Mercedes, etc в связке с числами
print("\nПопытка 2: Поиск паттернов с известными марками...")
known_brands = ['BMW', 'Mercedes', 'Opel', 'Nissan', 'Toyota', 'Honda']
for brand in known_brands:
    # Ищем паттерн типа "3": "BMW" или {id: 3, name: "BMW"}
    patterns = [
        rf'"(\d+)":\s*"{brand}"',
        rf'{{"id":\s*(\d+),\s*"name":\s*"{brand}"',
        rf'value="(\d+)"[^>]*>{brand}<',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"  {brand}: man_id = {matches[0]}")
            break

print("\nПопытка 3: Поиск API эндпоинтов в HTML...")
api_urls = re.findall(r'(https://api\d*\.myauto\.ge/[^\s"\']+)', html)
unique_urls = sorted(set(api_urls))
print(f"Найдено уникальных API URL: {len(unique_urls)}")
for url in unique_urls[:10]:
    print(f"  {url}")

print("\nПопытка 4: Прямой запрос к /getManufacturers с разными параметрами...")
endpoints = [
    'https://api2.myauto.ge/ka/getManufacturers',
    'https://api2.myauto.ge/en/getManufacturers',
    'https://api2.myauto.ge/ka/manufacturers',
    'https://api2.myauto.ge/en/manufacturers',
    'https://api2.myauto.ge/ka/makes',
    'https://api2.myauto.ge/en/makes',
]

for endpoint in endpoints:
    try:
        resp = scraper.get(endpoint, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data and (isinstance(data, list) or (isinstance(data, dict) and data)):
                print(f"\n✅ НАЙДЕН: {endpoint}")
                print(f"Тип данных: {type(data)}")
                if isinstance(data, list):
                    print(f"Количество элементов: {len(data)}")
                    if len(data) > 0:
                        print(f"Первый элемент: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Ключи: {list(data.keys())}")
                    for key in data:
                        if isinstance(data[key], list) and len(data[key]) > 0:
                            print(f"  {key}: {len(data[key])} элементов")
                            print(f"  Первый: {data[key][0]}")
                break
    except Exception as e:
        pass

print("\nПопытка 5: Проверка конкретных объявлений...")
# Берем реальные man_id из наших данных
real_man_ids = [1, 2, 3, 12, 16, 19, 22, 39, 41, 352, 394]
# Попробуем загрузить фильтр с конкретной маркой
for man_id in real_man_ids[:3]:
    try:
        url = f'https://api2.myauto.ge/ka/products/'
        params = {'TypeID': 0, 'PerPage': 1, 'MakeID': man_id}
        resp = scraper.get(url, params=params, timeout=5)
        data = resp.json()
        if 'data' in data and 'items' in data['data'] and len(data['data']['items']) > 0:
            item = data['data']['items'][0]
            print(f"man_id {man_id}: car_model = {item.get('car_model', 'N/A')}")
    except Exception as e:
        pass

print("\n" + "="*80)
print("Попытка завершена. Проверьте myauto_page.html для ручного анализа.")
