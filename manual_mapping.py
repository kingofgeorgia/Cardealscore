import json

# Загружаем данные
with open('cars_data.json', encoding='utf-8') as f:
    cars = json.load(f)

# Группируем автомобили по man_id
by_man_id = {}
for car in cars:
    man_id = car['make']
    if man_id not in by_man_id:
        by_man_id[man_id] = []
    by_man_id[man_id].append(car)

print("Анализ моделей для определения марок")
print("="*80)

# Ручной анализ на основе характерных моделей
brand_detection = {
    # Определяем по характерным моделям
    3: ('BMW', ['xDrive', 'sDrive', 'iX', 'M Sport', '328', 'X5', 'X3']),
    2: ('Audi', ['quattro', 'Premium Plus', 'Q5', 'Q3', 'Q7', 'A4', 'A6']),
    5: ('Chevrolet', ['LT Auto', 'Cruze', 'Malibu', 'Tahoe', 'Silverado']),
    10: ('Dodge', ['SRT', 'Challenger', 'Charger', 'Durango', 'Hemi']),
    19: ('Jeep', ['Rubicon', 'Wrangler', 'Cherokee', 'Grand Cherokee', 'Laredo']),
    22: ('Land Rover', ['R-Dynamic', 'Range Rover', 'Discovery', 'Defender', 'Evoque']),
    23: ('Lexus', ['F sport', 'RX', 'GX', 'LX', 'ES', 'NX', 'IS']),
    28: ('MINI', ['Cooper', 'S-ALL4', 'Countryman', 'Clubman']),
    29: ('Mitsubishi', ['SPORTERO', 'Outlander', 'Pajero', 'L200', 'ASX']),
    39: ('Subaru', ['Impreza', 'Legacy', 'Outback', 'Forester', 'Crosstrek', 'Ascent', 'WRX', 'i Limited']),
    155: ('Tesla', ['Model', 'LONG RANGE', 'DUAL MOTOR', 'Performance']),
    41: ('Toyota', ['Land Cruiser', 'Prado', 'Camry', 'RAV', '4 Runner', 'Highlander', 'Corolla', 'Tundra', 'Tacoma']),
    1: ('Mercedes-Benz', ['AMG', 'E-Class', 'C-Class', 'GLE', 'GLC', 'S-Class', 'CLA']),
    7: ('Ford', ['Mustang', 'F-150', 'Explorer', 'Escape', 'Focus', 'Fusion', 'Expedition', 'C-MAX']),
    11: ('GMC', ['Sierra', 'Yukon', 'Terrain', 'Acadia']),
    12: ('Honda', ['Civic', 'Accord', 'CR-V', 'Pilot', 'Odyssey', 'HR-V']),
    14: ('Hyundai', ['Sonata', 'Tucson', 'Santa Fe', 'Elantra', 'Kona']),
    16: ('Infiniti', ['Q50', 'Q60', 'QX', 'G37', 'M37']),
    18: ('Jaguar', ['XF', 'XE', 'F-Type', 'F-Pace', 'Supercharged']),
    20: ('Kia', ['Optima', 'Sorento', 'Sportage', 'Soul', 'Forte', 'Telluride']),
    24: ('Mazda', ['CX-5', 'CX-9', 'Mazda3', 'Mazda6', 'MX-5']),
    25: ('Mercedes-AMG', ['GT', 'C63', 'E63', 'GLE63', 'S63']),
    30: ('Nissan', ['Altima', 'Rogue', 'Pathfinder', 'Maxima', 'Sentra', 'Murano', 'Frontier', 'Titan']),
    31: ('Opel', ['Astra', 'Insignia', 'Corsa', 'Mokka']),
    33: ('Porsche', ['Cayenne', 'Macan', '911', 'Panamera', 'Taycan']),
    34: ('Renault', ['Duster', 'Captur', 'Megane', 'Clio']),
    38: ('Skoda', ['Octavia', 'Superb', 'Kodiaq', 'Karoq']),
    42: ('Volkswagen', ['Golf', 'Passat', 'Tiguan', 'Jetta', 'Caddy', 'Touareg']),
    43: ('Volvo', ['XC90', 'XC60', 'S60', 'S90', 'V60']),
    53: ('Chrysler', ['300', 'Pacifica', 'Town & Country']),
    61: ('Smart', ['Fortwo', 'Forfour']),
    75: ('Maserati', ['Ghibli', 'Levante', 'Quattroporte']),
    89: ('BYD', ['Tang', 'Han', 'Seal']),
    110: ('Hummer', ['H2', 'H3']),
    124: ('Polestar', ['2', '3']),
    161: ('Zeekr', ['001', '009', 'X']),
    394: ('Bentley', ['Continental', 'Flying Spur', 'Bentayga']),
    786: ('Alfa Romeo', ['Giulia', 'Stelvio', '159']),
    987: ('Can-Am', ['Spyder', 'Ryker']),
}

# Проверяем наши предположения 
correct_brands = {}

for man_id, cars_list in sorted(by_man_id.items()):
    detected_brand = None
    
    if man_id in brand_detection:
        expected_brand, patterns = brand_detection[man_id]
        
        # Проверяем модели
        models = [c.get('model', '') for c in cars_list[:5]]  # Первые 5 моделей
        
        match_found = False
        for model in models:
            model_lower = model.lower()
            for pattern in patterns:
                if pattern.lower() in model_lower:
                    match_found = True
                    break
            if match_found:
                break
        
        if match_found or not any(models):  # Если нашли паттерн или модели пустые
            detected_brand = expected_brand
            correct_brands[man_id] = expected_brand
            print(f"man_id={man_id:3} → {expected_brand:20} ✅")
        else:
            print(f"man_id={man_id:3} → {expected_brand:20} ⚠️  (модели: {', '.join(m[:20] for m in models if m)})")
    else:
        # Неизвестная марка
        models = [c.get('model', '') for c in cars_list[:3]]
        print(f"man_id={man_id:3} → UNKNOWN              ❓  (модели: {', '.join(m[:20] for m in models if m)})")

print("\n" + "="*80)
print(f"Определено {len(correct_brands)} марок")
print("="*80)

# Генерируем Python код
print("\n# Правильный MAKE_NAMES для parser.py:")
print("MAKE_NAMES = {")
for man_id in sorted(correct_brands.keys()):
    print(f"    {man_id}: '{correct_brands[man_id]}',")
print("}")

# Сохраняем
with open('correct_make_names.json', 'w', encoding='utf-8') as f:
    json.dump(correct_brands, f, ensure_ascii=False, indent=2)

print("\n✅ Сохранено в correct_make_names.json")
