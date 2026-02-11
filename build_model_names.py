"""
Построение словаря MODEL_NAMES на основе реальных данных
Используем анализ автомобилей и ручную расшифровку популярных моделей
"""
import json
from collections import Counter

# Загружаем текущие данные
with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

print("="*80)
print("АНАЛИЗ МОДЕЛЕЙ")
print("="*80)

# Подсчитываем статистику по model_id
model_stats = Counter()
model_info = {}  # model_id -> {make_name, trim_examples, count}

for car in cars:
    model_id = car.get('model_id')
    if model_id:
        model_stats[model_id] += 1
        
        if model_id not in model_info:
            model_info[model_id] = {
                'make_name': car.get('make_name', 'Unknown'),
                'trims': [],
                'count': 0
            }
        
        model_info[model_id]['count'] += 1
        trim = car.get('trim', '').strip()
        if trim and trim not in model_info[model_id]['trims']:
            model_info[model_id]['trims'].append(trim)

# Топ-30 самых популярных моделей
print(f"\nВсего уникальных моделей: {len(model_stats)}")
print(f"Топ-30 самых популярных моделей:\n")

top_models = model_stats.most_common(30)

print(f"{'#':3} {'Model ID':>10} {'Count':>6} {'Make':20} {'Trim Examples'}")
print("-"*80)

for idx, (model_id, count) in enumerate(top_models, 1):
    info = model_info[model_id]
    make = info['make_name']
    trim_sample = info['trims'][0][:35] if info['trims'] else '(нет trim)'
    
    print(f"{idx:3}. {model_id:8} {count:5}x  {make:18} {trim_sample}")

# Известные модели (расшифровка вручную на основе знаний о популярных авто)
print("\n" + "="*80)
print("ПРЕДЛОЖЕНИЕ: СЛОВАРЬ MODEL_NAMES")
print("="*80)

# Известные популярные модели (нужно проверить и дополнить)
known_models = {
    # Toyota
    1089: 'Camry',
    1128: 'Avalon', # возможно - нужно проверить по trim
    1124: 'Prius',
    1499: 'Highlander',
    1131: 'Corolla',
    1130: 'RAV4',
    
    # BMW
    103: 'X5',
    104: 'X3',
    99: '5 Series',
    98: '3 Series',
    108: 'X6',
    
    # Mercedes
    2239: 'E-Class',
    
    # Lexus
    16997: 'RX',
    361: 'ES',
    364: 'GX',
    
    # Jeep
    446: 'Wrangler',
    
    # Tesla
    1994: 'Model 3',
    1995: 'Model Y',
    1993: 'Model S',
    
    # Другие
    410: 'QX60',  # Infiniti
    2146: 'Tucson',  # Hyundai
    1625: 'Cayenne',  # Porsche
    2101: 'Giulia',  # Alfa Romeo
}

print("\nMODEL_NAMES = {")
for model_id, count in top_models[:30]:
    info = model_info[model_id]
    make = info['make_name']
    name = known_models.get(model_id, f'Unknown-{model_id}')
    
    # Подсказки для идентификации
    trims_hint = " | ".join(info['trims'][:2]) if info['trims'] else "нет trim"
    
    print(f"    {model_id}: '{name}',  # {make}, {count}x, trim: {trims_hint[:50]}")

print("}")

print("\n" + "="*80)
print("ДЕЙСТВИЯ:")
print("="*80)
print("""
1. Скопируйте словарь MODEL_NAMES выше
2. Исправьте названия моделей, где написано 'Unknown-XXX'
3. Добавьте в parser.py
4. Обновите код для использования MODEL_NAMES[model_id]
5. Перезапустите parser.py
""")

# Дополнительно: покажем примеры по каждой марке
print("\n" + "="*80)
print("ПРИМЕРЫ ПО МАРКАМ (для проверки):")
print("="*80)

from collections import defaultdict
by_make = defaultdict(list)

for model_id, count in top_models[:30]:
    info = model_info[model_id]
    by_make[info['make_name']].append((model_id, count, info['trims'][:2]))

for make in sorted(by_make.keys()):
    print(f"\n{make}:")
    for model_id, count, trims in by_make[make]:
        name = known_models.get(model_id, '???')
        trim_str = ", ".join(trims[:2]) if trims else ""
        print(f"  #{model_id:5} ({count:2}x) → {name:15} | {trim_str[:50]}")
