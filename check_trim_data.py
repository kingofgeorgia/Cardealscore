import json

with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Фильтруем автомобили с заполненным Trim
trimmed = [c for c in cars if c.get('trim')]

print(f'Всего автомобилей: {len(cars)}')
print(f'С заполненным Trim: {len(trimmed)}')
print(f'Без Trim: {len(cars) - len(trimmed)}')
print('\n' + '='*80)
print('Примеры с Trim:')
print('='*80)

for idx, car in enumerate(trimmed[:20]):
    make = car.get('make_name', 'N/A')
    model_id = car.get('model_id', 'N/A')
    model = car.get('model', '')
    trim = car.get('trim', '')
    
    print(f"{idx+1:2}. {make:18} | Model ID: #{model_id:4} | Trim: {trim[:40]}")

print('\n' + '='*80)
print('Статистика по model_id:')
print('='*80)

from collections import Counter
model_ids = Counter([c.get('model_id') for c in cars if c.get('model_id')])

print(f'\nУникальных model_id: {len(model_ids)}')
print('Топ 10 самых популярных:')
for model_id, count in model_ids.most_common(10):
    # Найдем пример автомобиля с этим model_id
    example = next(c for c in cars if c.get('model_id') == model_id)
    print(f"  #{model_id:4} : {count:2} авто | Марка: {example['make_name']:15} | Trim пример: {example.get('trim', 'N/A')[:30]}")
