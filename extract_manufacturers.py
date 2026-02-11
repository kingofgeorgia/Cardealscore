import cloudscraper
import re
import json

scraper = cloudscraper.create_scraper()

print("Загружаем страницу поиска myauto.ge...")
url = 'https://www.myauto.ge'
response = scraper.get(url, timeout=15)
html = response.text

print(f"Размер HTML: {len(html)} байт\n")

# Ищем переменную с данными о марках в JavaScript
# Обычно это window.manufacturers = [...] или подобное
patterns = [
    r'window\.manufacturers\s*=\s*(\[.*?\]);',
    r'var\s+manufacturers\s*=\s*(\[.*?\]);',
    r'const\s+manufacturers\s*=\s*(\[.*?\]);',
    r'"manufacturers":\s*(\[.*?\])',
]

found = False
for pattern in patterns:
    matches = re.findall(pattern, html, re.DOTALL)
    if matches:
        print(f"✅ Найден паттерн: {pattern[:50]}...")
        data_str = matches[0]
        
        # Пробуем распарсить JSON
        try:
            # Убираем возможные комментарии и лишние символы
            data_str = re.sub(r'//.*', '', data_str)
            data = json.loads(data_str)
            
            print(f"Количество марок: {len(data)}\n")
            print("Первые 20 марок:")
            for item in data[:20]:
                print(f"  {item}")
            
            # Сохраняем в файл
            with open('manufacturers_from_js.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("\nДанные сохранены в manufacturers_from_js.json")
            found = True
            break
        except Exception as e:
            print(f"Ошибка парсинга JSON: {e}")

if not found:
    print("❌ Не удалось найти данные о марках через JavaScript")
    print("\nПопробуем извлечь из HTML select...")
    
    # Ищем select с id или name связанным с производителем
    select_patterns = [
        r'<select[^>]*(?:id|name)=["\']?(?:make|manufacturer|man).*?>(.*?)</select>',
        r'<option[^>]*value=["\'](\d+)["\'][^>]*>([^<]+)</option>',
    ]
    
    for pattern in select_patterns:
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"\n✅ Найдено {len(matches)} опций")
            print("Первые 20:")
            for match in matches[:20]:
                if isinstance(match, tuple):
                    print(f"  {match[0]}: {match[1].strip()}")
                else:
                    print(f"  {match[:100]}")
            break

print("\n" + "="*80)
print("Альтернативный метод: извлекаем марки из HTML элементов")
print("="*80)

# Ищем все упоминания марок в ссылках типа /ka/s/manqanebi-bmw
brand_links = re.findall(r'/ka/s/manqanebi-([a-z-]+)', html)
if brand_links:
    brands_from_links = set(brand_links)
    print(f"\nНайдено {len(brands_from_links)} уникальных марок в ссылках:")
    for brand in sorted(brands_from_links)[:30]:
        print(f"  {brand}")
