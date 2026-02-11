"""
Проверка API деталей объявления myauto.ge
Цель: найти название модели в детальном API
"""
import cloudscraper
import json

scraper = cloudscraper.create_scraper()

# Получаем список автомобилей
list_url = 'https://api2.myauto.ge/en/products?vehicleType=0&ForRent=&Mans=&PriceFrom=600&PriceTo=50000&CurrencyID=1&MileageType=1&Customs=1&Page=1'
response = scraper.get(list_url, timeout=10)
cars = response.json()["data"]["items"]

print("="*80)
print("ПРОВЕРКА API ДЕТАЛЕЙ")
print("="*80)

# Берем первые 5 автомобилей для теста
for idx, car in enumerate(cars[:5], 1):
    car_id = car['car_id']
    man_id = car['man_id']
    model_id = car['model_id']
    
    print(f"\n{idx}. car_id={car_id}, man_id={man_id}, model_id={model_id}")
    
    # Пробуем разные варианты API для деталей
    detail_urls = [
        f"https://api2.myauto.ge/en/product/{car_id}",
        f"https://api2.myauto.ge/en/pr/{car_id}",
        f"https://api2.myauto.ge/product/{car_id}",
    ]
    
    for url in detail_urls:
        try:
            detail_response = scraper.get(url, timeout=10)
            if detail_response.status_code == 200:
                try:
                    detail_data = detail_response.json()
                    print(f"   ✅ Успешно: {url}")
                    
                    # Ищем поля с названием модели
                    model_fields = {k: v for k, v in detail_data.items() 
                                  if isinstance(k, str) and ('model' in k.lower() or 'name' in k.lower())}
                    
                    if model_fields:
                        print(f"   📋 Найденные поля:")
                        for key, value in model_fields.items():
                            print(f"      {key}: {value}")
                    
                    # Показываем все ключи верхнего уровня
                    print(f"   📦 Доступные ключи: {list(detail_data.keys())[:20]}")
                    break
                except json.JSONDecodeError:
                    print(f"   ⚠️  Не JSON: {url}")
        except Exception as e:
            print(f"   ❌ Ошибка {url}: {e}")

# Альтернатива: парсинг HTML страницы
print("\n" + "="*80)
print("АЛЬТЕРНАТИВА: ПАРСИНГ URL SLUG")
print("="*80)

# Проверим, есть ли паттерн в URL страниц
for idx, car in enumerate(cars[:10], 1):
    car_id = car['car_id']
    man_id = car['man_id']
    model_id = car['model_id']
    
    # URL может быть вида: https://www.myauto.ge/en/pr/{car_id}/{brand}-{model}-...
    page_url = f"https://www.myauto.ge/en/pr/{car_id}"
    
    try:
        page_response = scraper.get(page_url, timeout=10, allow_redirects=True)
        if page_response.status_code == 200:
            # Проверяем финальный URL после редиректа
            final_url = page_response.url
            print(f"{idx:2}. model_id={model_id} → {final_url}")
            
            # Извлекаем slug из URL
            import re
            slug_match = re.search(r'/pr/\d+/([^/?]+)', final_url)
            if slug_match:
                slug = slug_match.group(1)
                print(f"    Slug: {slug}")
    except Exception as e:
        print(f"{idx:2}. Ошибка: {e}")

print("\n" + "="*80)
print("РЕКОМЕНДАЦИЯ:")
print("="*80)
print("""
Если API деталей не содержит названия модели, можем:
1. Парсить slug из URL (например, 'toyota-camry-xle')
2. Построить словарь MODEL_NAMES вручную для топ-моделей
3. Оставить как есть (#model_id) и добавить расшифровку по запросу
""")
