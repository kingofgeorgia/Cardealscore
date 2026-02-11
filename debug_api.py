#!/usr/bin/env python
"""Debug the API response."""

import cloudscraper
from fake_useragent import UserAgent

scraper = cloudscraper.create_scraper()
ua = UserAgent()

scraper.headers.update({
    'User-Agent': ua.random,
    'Accept': 'application/json',
})

try:
    print("Запрашиваю API myauto.ge...")
    response = scraper.get(
        "https://api2.myauto.ge/en/products",
        params={
            'vehicleType': 0,
            'Page': 1,
        },
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.content)}")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"✓ Получен JSON массив с {len(data)} элементами")
            if data:
                print(f"Первый элемент: {data[0].get('make_name')} {data[0].get('model')} ({data[0].get('car_id')})")
        else:
            print(f"✗ Неожиданный тип данных: {type(data)}")
            print(f"Данные: {str(data)[:200]}")
    else:
        print(f"✗ Ошибка: {response.status_code}")
        print(f"Ответ: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
