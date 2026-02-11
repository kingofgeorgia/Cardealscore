#!/usr/bin/env python3
import cloudscraper
import json

scraper = cloudscraper.create_scraper()

# Получаем данные с первой страницы
url = 'https://api2.myauto.ge/en/products?vehicleType=0&Page=1'
response = scraper.get(url, timeout=10)
data = response.json()

print('='*80)
print('ПРОВЕРКА РЕАЛЬНЫХ МАРОК ИЗ API')
print('='*80)

# Собираем уникальные man_id с примерами
man_examples = {}
for car in data['data']['items'][:30]:
    man_id = car.get('man_id')
    car_model = car.get('car_model', '')
    
    if man_id and man_id not in man_examples:
        man_examples[man_id] = car_model[:30] if car_model else 'N/A'

print(f'\nНайдено уникальных man_id: {len(man_examples)}')
print('\nПримеры с моделями:')
for man_id, model in sorted(man_examples.items()):
    print(f'  man_id={man_id:3d} -> модель: {model}')

# Получаем справочник марок напрямую из API
print('\n' + '='*80)
print('ПОЛУЧЕНИЕ СПРАВОЧНИКА МАРОК')
print('='*80)

# Попробуем получить список марок
try:
    makes_url = 'https://api2.myauto.ge/en/getManufacturers'
    makes_response = scraper.get(makes_url, timeout=10)
    makes_data = makes_response.json()
    
    print(f'\nПолучено марок: {len(makes_data.get("data", []))}')
    print('\nПервые 30 марок:')
    
    for make in makes_data.get('data', [])[:30]:
        make_id = make.get('man_id')
        make_name = make.get('man_name') or make.get('name')
        print(f'  {make_id:3d}: {make_name}')
        
except Exception as e:
    print(f'Ошибка получения справочника: {e}')
