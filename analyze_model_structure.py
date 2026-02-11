import cloudscraper
import json

scraper = cloudscraper.create_scraper()

# Берем несколько разных объявлений
car_ids = [120496862, 120492134, 120452939]

print("Анализ структуры данных объявлений")
print("="*80)

for car_id in car_ids:
    try:
        url = f'https://api2.myauto.ge/ka/products/{car_id}'
        response = scraper.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            info = data.get('data', {}).get('info', {})
            
            print(f"\ncar_id: {car_id}")
            print(f"  man_id: {info.get('man_id')}")
            print(f"  model_id: {info.get('model_id')}")
            print(f"  car_model: '{info.get('car_model')}'")
            
            # Проверяем есть ли другие поля с моделью
            model_fields = {k: v for k, v in info.items() if 'model' in k.lower() or 'trim' in k.lower()}
            if model_fields:
                print("  Все поля с model/trim:")
                for k, v in model_fields.items():
                    print(f"    {k}: {v}")
                    
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")

print("\n" + "="*80)
print("ВЫВОД:")
print("="*80)
print("""
В API myauto.ge:
- man_id: ID марки (например 1 = Alfa Romeo)
- model_id: ID модели (например 2101 = Stelvio)
- car_model: Trim/комплектация (например "TI", "Sport", "xDrive50i")

Проблема: Нет прямого API для получения названия модели по model_id.

РЕШЕНИЕ:
1. Извлекать название модели из текста объявления (description)
2. Или строить справочник model_id → model_name эмпирически
3. Или использовать car_model как есть (это Trim, но лучше чем ничего)

Рекомендация: 
- Показывать Марку (man_id → MAKE_NAMES)
- Показывать Model как model_id (цифра)
- Показывать Trim как car_model (текст комплектации)
""")

# Попробуем построить маппинг model_id → model_name из базы
print("\n" + "="*80)
print("Попытка построить маппинг из базы данных...")
print("="*80)

with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Группируем по model_id
from collections import defaultdict
models_by_id = defaultdict(list)

for car in cars[:50]:  # Первые 50
    # Получаем детали
    car_id = car.get('car_id')
    if not car_id:
        continue
    
    try:
        url = f'https://api2.myauto.ge/ka/products/{car_id}'
        response = scraper.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            info = data.get('data', {}).get('info', {})
            
            man_id = info.get('man_id')
            model_id = info.get('model_id')
            car_model = info.get('car_model', '')
            
            if model_id:
                models_by_id[model_id].append({
                    'man_id': man_id,
                    'car_model': car_model,
                    'car_id': car_id
                })
                
                print(f"model_id={model_id}: man_id={man_id}, car_model='{car_model}'")
    except:
        pass

print(f"\nСобрано {len(models_by_id)} уникальных model_id")
