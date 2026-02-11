"""
Проверка заполненности названий моделей после обновления
"""
import json
from collections import Counter

with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

print("="*80)
print("СТАТИСТИКА НАЗВАНИЙ МОДЕЛЕЙ")
print("="*80)

# Подсчет
total = len(cars)
with_model_name = sum(1 for c in cars if c.get('model', '').strip())
without_model_name = total - with_model_name

print(f"\n📊 Всего автомобилей: {total}")
print(f"✅ С названием модели: {with_model_name} ({with_model_name/total*100:.1f}%)")
print(f"⚠️  Без названия модели: {without_model_name} ({without_model_name/total*100:.1f}%)")

# Примеры с названиями
print("\n" + "="*80)
print("ПРИМЕРЫ С НАЗВАНИЯМИ МОДЕЛЕЙ:")
print("="*80)

examples_with = [c for c in cars if c.get('model', '').strip()][:20]
print(f"\n{'#':3} {'Make':18} {'Model':15} {'Trim'[:30]}")
print("-"*80)

for idx, car in enumerate(examples_with, 1):
    make = car.get('make_name', 'Unknown')
    model = car.get('model', '')
    trim = car.get('trim', '')[:30]
    print(f"{idx:3}. {make:18} {model:15} {trim}")

# Примеры БЕЗ названий
print("\n" + "="*80)
print("ПРИМЕРЫ БЕЗ НАЗВАНИЙ (будут показаны как #ID):")
print("="*80)

examples_without = [c for c in cars if not c.get('model', '').strip()][:15]
print(f"\n{'#':3} {'Make':18} {'Model ID':10} {'Trim'[:30]}")
print("-"*80)

for idx, car in enumerate(examples_without, 1):
    make = car.get('make_name', 'Unknown')
    model_id = car.get('model_id', 'N/A')
    trim = car.get('trim', '')[:30]
    print(f"{idx:3}. {make:18} #{model_id:<9} {trim}")

# Топ моделей
print("\n" + "="*80)
print("ТОП-15 ПОПУЛЯРНЫХ МОДЕЛЕЙ:")
print("="*80)

model_counter = Counter()
model_info = {}

for car in cars:
    model_name = car.get('model', '').strip()
    if model_name:
        model_counter[model_name] += 1
        if model_name not in model_info:
            model_info[model_name] = {
                'make': car.get('make_name', 'Unknown'),
                'model_id': car.get('model_id', 'N/A')
            }

print(f"\n{'#':3} {'Model':15} {'Make':18} {'Count':>6}")
print("-"*80)

for idx, (model, count) in enumerate(model_counter.most_common(15), 1):
    info = model_info[model]
    make = info['make']
    print(f"{idx:3}. {model:15} {make:18} {count:5}x")

print("\n" + "="*80)
print("✅ ГОТОВО К ЗАПУСКУ GUI!")
print("="*80)
print("\nЗапустите: python app.py")
print("\nКолонка 'Модель' теперь показывает:")
print("  - Название модели (Camry, X5, Wrangler) - если есть в словаре")
print("  - #model_id - если нет в словаре")
