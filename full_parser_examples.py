#!/usr/bin/env python
"""
Examples of using the full site parser.

Примеры использования полного парсера myauto.ge.
"""

from mileon_saas.services.full_site_parser import FullSiteParser
import json


def example1_basic_parsing():
    """Пример 1: Базовый парсинг первых 3 страниц."""
    print("=" * 60)
    print("ПРИМЕР 1: Парсинг первых 3 страниц")
    print("=" * 60)
    
    parser = FullSiteParser(delay_seconds=2.0)
    
    print("Начинаю парсинг...")
    parser.parse_all_pages(max_pages=3)
    
    print(f"✓ Загружено {len(parser.all_listings)} объявлений")
    
    if parser.all_listings:
        first = parser.all_listings[0]
        print(f"\nПервое объявление:")
        print(f"  - Марка: {first.get('make_name')}")
        print(f"  - Модель: {first.get('model')}")
        print(f"  - Год: {first.get('year')}")
        print(f"  - Цена: ${first.get('price_usd')}")
        
        # Save
        output = parser.save_to_file("example1_3_pages.json")
        print(f"\nСохранено в: {output}")


def example2_with_progress():
    """Пример 2: Парсинг с отслеживанием прогресса."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Парсинг с прогресс-баром")
    print("=" * 60)
    
    def show_progress(count, elapsed):
        """Show progress every time count changes."""
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        secs = int(elapsed % 60)
        print(f"  [{count:5d}] объявлений загружено | {hours:02d}:{minutes:02d}:{secs:02d} прошло")
    
    parser = FullSiteParser(delay_seconds=0.5, progress_callback=show_progress)
    
    print("Начинаю парсинг (первые 2 страницы с быстрой задержкой)...")
    parser.parse_all_pages(max_pages=2)
    
    print(f"\n✓ Готово! Загружено: {len(parser.all_listings)} объявлений")


def example3_analyze_data():
    """Пример 3: Анализ полученных данных."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Анализ загруженных данных")
    print("=" * 60)
    
    parser = FullSiteParser(delay_seconds=1.0)
    
    print("Загружаю данные (первая страница)...")
    parser.parse_all_pages(max_pages=1)
    
    if not parser.all_listings:
        print("Нет данных для анализа")
        return
    
    data = parser.all_listings
    
    # Статистика по маркам
    makes = {}
    for car in data:
        make = car.get('make_name', 'Unknown')
        makes[make] = makes.get(make, 0) + 1
    
    print(f"\nВсего объявлений: {len(data)}")
    print(f"Уникальных марок: {len(makes)}")
    
    print("\nТоп 5 марок по количеству:")
    for make, count in sorted(makes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {make:20s}: {count:3d}")
    
    # Ценовая статистика
    prices = [car.get('price_usd', 0) for car in data if car.get('price_usd')]
    if prices:
        print(f"\nЦены:")
        print(f"  Минимум: ${min(prices):,.0f}")
        print(f"  Максимум: ${max(prices):,.0f}")
        print(f"  Средняя: ${sum(prices) / len(prices):,.0f}")


def example4_load_and_process():
    """Пример 4: Загрузка сохраненного файла и обработка."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Загрузка и обработка сохраненных данных")
    print("=" * 60)
    
    # First save some data
    parser = FullSiteParser(delay_seconds=1.0)
    print("Загружаю данные (первая страница)...")
    parser.parse_all_pages(max_pages=1)
    
    output_file = parser.save_to_file("example4_data.json")
    print(f"✓ Сохранено в: {output_file}")
    
    # Now load and process
    print(f"\nЗагружаю данные из файла...")
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Загружено {len(data)} объявлений")
    
    # Find expensive cars
    expensive = [car for car in data if car.get('price_usd', 0) > 40000]
    print(f"\nДорогих машин (>$40k): {len(expensive)}")
    for car in expensive[:3]:
        print(f"  - {car.get('make_name')} {car.get('model')} ({car.get('year')}): ${car.get('price_usd'):,.0f}")


def example5_custom_delay():
    """Пример 5: Парсинг с кастомной задержкой."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 5: Быстрый парсинг (1 сек задержка вместо 2)")
    print("=" * 60)
    
    # Используем меньшую задержку для теста
    parser = FullSiteParser(delay_seconds=1.0)
    
    print("Парсинг первой страницы с 1-секундной задержкой...")
    parser.parse_all_pages(max_pages=1)
    
    print(f"✓ Загружено {len(parser.all_listings)} объявлений")


if __name__ == "__main__":
    try:
        # Запустить пример 1
        example1_basic_parsing()
        
        # Запустить пример 2
        example2_with_progress()
        
        # Запустить пример 3
        example3_analyze_data()
        
        # Запустить пример 4
        example4_load_and_process()
        
        # Запустить пример 5
        example5_custom_delay()
        
        print("\n" + "=" * 60)
        print("✓ ВСЕ ПРИМЕРЫ ЗАВЕРШЕНЫ")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
