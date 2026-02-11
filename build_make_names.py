import json
import cloudscraper

# Загружаем существующие данные
with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Извлекаем уникальные man_id
man_ids = sorted(set(car['make'] for car in cars))
print(f"Уникальных man_id: {len(man_ids)}")
print(f"man_ids: {man_ids}\n")

# Создаем скрейпер
scraper = cloudscraper.create_scraper()

# Для каждого man_id получим детали одного автомобиля
# и попробуем извлечь марку из matching_parts
make_names = {}

print("Получаем названия марок из API детализации объявлений...")
print("="*80)

for man_id in man_ids:
    # Находим любой car_id с этим man_id
    car_with_man_id = next((c for c in cars if c['make'] == man_id), None)
    if not car_with_man_id:
        continue
    
    car_id = car_with_man_id['car_id']
    
    try:
        print(f"man_id={man_id:3} | car_id={car_id} | ", end='', flush=True)
        
        # Запрашиваем детали
        url = f'https://api2.myauto.ge/ka/products/{car_id}'
        response = scraper.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Проверяем matching_parts
            if 'data' in data and 'matching_parts' in data['data']:
                parts = data['data']['matching_parts'].get('parts', [])
                
                if parts:
                    # Берем первую деталь
                    first_part = parts[0]
                    part_name = first_part.get('part_name', '')
                    
                    # Пробуем извлечь марку из названия детали
                    # Обычно это первое слово или словосочетание
                    # Например: "Alfa Romeo Stelvio" -> "Alfa Romeo"
                    brand_candidates = []
                    
                    # Известные двухсловные марки
                    two_word_brands = ['Alfa Romeo', 'Land Rover', 'Range Rover', 'Mercedes-Benz', 'Mercedes Benz']
                    
                    for brand in two_word_brands:
                        if brand.lower() in part_name.lower():
                            brand_candidates.append(brand)
                            break
                    
                    if not brand_candidates:
                        # Берем первое слово
                        words = part_name.split()
                        if words:
                            brand_candidates.append(words[0])
                    
                    if brand_candidates:
                        make_name = brand_candidates[0]
                        make_names[man_id] = make_name
                        print(f"✅ {make_name}")
                    else:
                        print(f"⚠️  Не найдено название (part_name={part_name[:30]})")
                else:
                    print("⚠️  Нет деталей")
            else:
                print("⚠️  Нет matching_parts")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

print("\n" + "="*80)
print(f"Определено {len(make_names)} марок из {len(man_ids)}")
print("="*80)

# Выводим результат
print("\nОпределенные марки:")
for man_id in sorted(make_names.keys()):
    print(f"{man_id:3} : {make_names[man_id]}")

# Сохраняем
with open('make_names_detected.json', 'w', encoding='utf-8') as f:
    json.dump(make_names, f, ensure_ascii=False, indent=2)

print("\n✅ Данные сохранены в make_names_detected.json")

# Создаем Python словарь для parser.py
print("\n" + "="*80)
print("Python код для parser.py:")
print("="*80)
print("\nMAKE_NAMES = {")
for man_id in sorted(make_names.keys()):
    print(f"    {man_id}: '{make_names[man_id]}',")
print("}")
