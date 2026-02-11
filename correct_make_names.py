# Правильный маппинг man_id → название марки
# Построен на основе анализа реальных данных из API myauto.ge

MAKE_NAMES = {
    1: 'Alfa Romeo',
    2: 'Audi',
    3: 'BMW',
    5: 'Chevrolet',
    7: 'Ford',
    10: 'Dodge',
    11: 'GMC',
    12: 'Honda',
    14: 'Hyundai',
    16: 'Infiniti',
    18: 'Jaguar',
    19: 'Jeep',
    20: 'Kia',
    22: 'Land Rover',
    23: 'Lexus',
    24: 'Mazda',
    25: 'Mercedes-AMG',
    28: 'MINI',
    29: 'Mitsubishi',
    30: 'Nissan',
    31: 'Opel',
    33: 'Porsche',
    34: 'Renault',
    38: 'Skoda',
    39: 'Subaru',
    41: 'Toyota',
    42: 'Volkswagen',
    43: 'Volvo',
    53: 'Chrysler',
    61: 'Smart',
    75: 'Maserati',
    89: 'BYD',
    110: 'Hummer',
    124: 'Polestar',
    155: 'Tesla',
    161: 'Zeekr',
    394: 'Bentley',
    786: 'Alfa Romeo',  # Тоже Alfa Romeo (возможно другая модельная линейка)
    987: 'Can-Am',
}

print("Правильный MAKE_NAMES словарь создан!")
print(f"Всего марок: {len(MAKE_NAMES)}")
