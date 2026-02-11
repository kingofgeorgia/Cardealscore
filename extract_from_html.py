import json
import cloudscraper
import time

# Загружаем существующие данные
with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Извлекаем уникальные man_id
man_ids = sorted(set(car['make'] for car in cars))
print(f"Уникальных man_id: {len(man_ids)}")

# Создаем скрейпер  
scraper = cloudscraper.create_scraper()

# Для каждого man_id получим HTML страницу объявления
# и попробуем извлечь марку из meta-тегов или заголовков
make_names = {}

print("\nПолучаем названия марок из HTML страниц объявлений...")
print("="*80)

for man_id in man_ids[:10]:  # Первые 10 для теста
    # Находим любой car_id с этим man_id
    car_with_man_id = next((c for c in cars if c['make'] == man_id), None)
    if not car_with_man_id:
        continue
    
    car_id = car_with_man_id['car_id']
    
    try:
        print(f"man_id={man_id:3} | car_id={car_id} | ", end='', flush=True)
        
        # Запрашиваем HTML страницу
        url = f'https://www.myauto.ge/ka/pr/{car_id}'
        response = scraper.get(url, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            
            # Ищем заголовок страницы - обычно содержит год - марка модель
            # Например: "2016 - BMW 328"
            import re
            
            # Паттерн для title который обычно содержит год - марка модель
            title_match = re.search(r'<title>([^<]+)</title>', html)
            if title_match:
                title = title_match.group(1)
                # Например: "2016 - BMW 328 | myauto.ge"
                # Убираем suffix and prefix
                title = title.split('|')[0].strip()
                # Формат: "YYYY - Марка Модель"
                parts = title.split(' - ')
                if len(parts) >= 2:
                    # parts[1] = "BMW 328"
                    brand_and_model = parts[1].strip()
                    # Берем первое слово (или два для составных марок)
                    words = brand_and_model.split()
                    
                    # Известные двухсловные марки
                    two_word_brands = {
                        'alfa romeo', 'land rover', 'range rover', 'mercedes-benz', 
                        'mercedes benz', 'aston martin', 'rolls royce'
                    }
                    
                    brand = None
                    if len(words) >= 2:
                        two_words = f"{words[0]} {words[1]}".lower()
                        if two_words in two_word_brands:
                            brand = words[0] + ' ' + words[1]
                        else:
                            brand = words[0]
                    elif len(words) == 1:
                        brand = words[0]
                    
                    if brand:
                        make_names[man_id] = brand
                        print(f"✅ {brand}")
                    else:
                        print(f"⚠️  Не распознано (title={title})")
                else:
                    print(f"⚠️  Неожиданный формат title: {title}")
            else:
                print(f"⚠️  Нет title тега")
        else:
            print(f"❌ HTTP {response.status_code}")
            
        # Задержка чтобы не перегружать сервер
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

print("\n" + "="*80)
print(f"Определено {len(make_names)} марок из {min(10, len(man_ids))}")
print("="*80)

# Выводим результат
if make_names:
    print("\nОпределенные марки:")
    for man_id in sorted(make_names.keys()):
        print(f"{man_id:3} : {make_names[man_id]}")
else:
    print("\n⚠️  Ни одной марки не определено")
    print("Потребуется ручной маппинг на основе известных марок")
