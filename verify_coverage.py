import json

# Загружаем cars_data.json
with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Загружаем parser.py чтобы получить MAKE_NAMES
import sys
import importlib.util
spec = importlib.util.spec_from_file_location("parser", "parser.py")
parser = importlib.util.module_from_spec(spec)

# Извлекаем MAKE_NAMES из кода вручную
with open('parser.py', encoding='utf-8') as f:
    parser_code = f.read()

# Ищем MAKE_NAMES
import re
match = re.search(r'MAKE_NAMES\s*=\s*\{([^}]+)\}', parser_code, re.DOTALL)
if match:
    make_names_str = '{' + match.group(1) + '}'
    # Преобразуем в dict
    exec(f"MAKE_NAMES = {make_names_str}")
else:
    print("❌ Не удалось извлечь MAKE_NAMES из parser.py")
    exit(1)

print("ПРОВЕРКА ПОКРЫТИЯ МАРОК")
print("="*80)

# Извлекаем все уникальные man_id из базы
man_ids_in_data = set(car['make'] for car in cars if car.get('make'))
man_ids_in_dict = set(MAKE_NAMES.keys())

print(f"Марок в базе данных: {len(man_ids_in_data)}")
print(f"Марок в словаре: {len(man_ids_in_dict)}")

# Проверяем покрытие
missing_in_dict = man_ids_in_data - man_ids_in_dict
extra_in_dict = man_ids_in_dict - man_ids_in_data

if missing_in_dict:
    print(f"\n⚠️  ОТСУТСТВУЮТ В СЛОВАРЕ ({len(missing_in_dict)}):")
    for man_id in sorted(missing_in_dict):
        # Найдем примеры авто с этой маркой
        examples = [c for c in cars if c.get('make') == man_id][:3]
        print(f"\n  man_id={man_id}:")
        for ex in examples:
            print(f"    ${ex['price_usd']:>6} | {ex['year']} | {ex['engine_volume']:>4}cc | model: {ex.get('model', '')[:40]}")
else:
    print("\n✅ Все марки из базы данных присутствуют в словаре!")

if extra_in_dict:
    print(f"\n📝 ЕСТЬ В СЛОВАРЕ, НО НЕ В БАЗЕ ({len(extra_in_dict)}):")
    for man_id in sorted(extra_in_dict):
        print(f"  {man_id:3}: {MAKE_NAMES[man_id]}")

# Проверяем качество названий
print("\n" + "="*80)
print("ТЕКУЩИЙ СЛОВАРЬ МАРОК:")
print("="*80)

for man_id in sorted(MAKE_NAMES.keys()):
    count = sum(1 for c in cars if c.get('make') == man_id)
    print(f"{man_id:3}: {MAKE_NAMES[man_id]:20} | Автомобилей в базе: {count}")

print("\n" + "="*80)
print("ИТОГОВАЯ СТАТИСТИКА:")
print("="*80)
total_cars = len(cars)
cars_with_make = sum(1 for c in cars if c.get('make') and c.get('make') in MAKE_NAMES)
coverage = (cars_with_make / total_cars * 100) if total_cars > 0 else 0

print(f"Всего автомобилей: {total_cars}")
print(f"С определенной маркой: {cars_with_make}")
print(f"Покрытие: {coverage:.1f}%")

if coverage == 100:
    print("\n✅ ОТЛИЧНО! Все марки правильно определены!")
elif coverage >= 95:
    print(f"\n✅ ХОРОШО! Покрытие {coverage:.1f}%")
else:
    print(f"\n⚠️  Требуется улучшение, покрытие только {coverage:.1f}%")
