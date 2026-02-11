"""
Скрипт для анализа полей API myauto.ge
Цель: найти поле с названием модели
"""
import cloudscraper
import json

scraper = cloudscraper.create_scraper()
url = 'https://api2.myauto.ge/en/products?vehicleType=0&ForRent=&Mans=&PriceFrom=600&PriceTo=50000&CurrencyID=1&MileageType=1&Customs=1&Page=1'

print("Запрашиваем данные из API...")
response = scraper.get(url, timeout=10)
data = response.json()

if data.get("data", {}).get("items"):
    items = data["data"]["items"]
    print(f"\n✅ Получено автомобилей: {len(items)}")
    print("\n" + "="*80)
    print("АНАЛИЗ ПЕРВОГО АВТОМОБИЛЯ:")
    print("="*80)
    
    first_car = items[0]
    print("\nВСЕ ДОСТУПНЫЕ ПОЛЯ:")
    print("-"*80)
    for key, value in sorted(first_car.items()):
        value_str = str(value)[:60] if value else "None"
        print(f"{key:25} : {value_str}")
    
    # Ищем поля, которые могут содержать название модели
    print("\n" + "="*80)
    print("ПОЛЯ, СВЯЗАННЫЕ С МОДЕЛЬЮ:")
    print("="*80)
    
    model_fields = {k: v for k, v in first_car.items() if 'model' in k.lower() or 'car' in k.lower()}
    for key, value in model_fields.items():
        print(f"{key:25} : {value}")
    
    # Проверяем URL объявления (там может быть slug с названием модели)
    print("\n" + "="*80)
    print("ПРОВЕРКА URL И SLUG:")
    print("="*80)
    
    car_id = first_car.get('car_id')
    man_id = first_car.get('man_id')
    model_id = first_car.get('model_id')
    
    # URL страницы автомобиля на myauto.ge
    detail_url = f"https://www.myauto.ge/en/pr/{car_id}"
    print(f"URL объявления: {detail_url}")
    
    # Попробуем запросить страницу и извлечь из нее название модели
    print("\nПопытка получить детали объявления...")
    try:
        detail_response = scraper.get(detail_url, timeout=10)
        if detail_response.status_code == 200:
            html = detail_response.text
            # Ищем паттерны с названием модели в HTML
            import re
            
            # Ищем в title
            title_match = re.search(r'<title>([^<]+)</title>', html)
            if title_match:
                print(f"Title страницы: {title_match.group(1)}")
            
            # Ищем og:title (Open Graph)
            og_title = re.search(r'og:title["\s]+content="([^"]+)"', html)
            if og_title:
                print(f"og:title: {og_title.group(1)}")
    except Exception as e:
        print(f"Ошибка при запросе деталей: {e}")
    
    # Показываем примеры для нескольких автомобилей
    print("\n" + "="*80)
    print("ПРИМЕРЫ АВТОМОБИЛЕЙ (первые 10):")
    print("="*80)
    print(f"{'man_id':>8} {'model_id':>10} {'car_model (trim)':40}")
    print("-"*80)
    
    for car in items[:10]:
        man_id = car.get('man_id', 'N/A')
        model_id = car.get('model_id', 'N/A')
        car_model = car.get('car_model', '')[:38]
        print(f"{man_id:>8} {model_id:>10} {car_model:40}")

else:
    print("❌ Не удалось получить данные")

print("\n" + "="*80)
print("ВЫВОД:")
print("="*80)
print("""
API myauto.ge возвращает:
- man_id: ID марки (используется в MAKE_NAMES)
- model_id: ID модели (числовой)
- car_model: Комплектация/Trim (текст)

❌ Название модели НЕ приходит напрямую из API списка.

✅ РЕШЕНИЯ:
1. Парсить URL объявлений (может содержать slug с названием модели)
2. Запросить API деталей: https://api2.myauto.ge/en/pr/{car_id}
3. Построить словарь MODEL_NAMES эмпирически для топ-моделей
""")
