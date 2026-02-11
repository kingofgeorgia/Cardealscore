#!/usr/bin/env python
"""Test full site parser functionality."""

from mileon_saas.services.full_site_parser import FullSiteParser

def progress_callback(count: int, elapsed: float):
    """Display progress."""
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    secs = int(elapsed % 60)
    print(f"  Загружено: {count} машин | {hours:02d}:{minutes:02d}:{secs:02d} прошло")

if __name__ == "__main__":
    parser = FullSiteParser(delay_seconds=2.0, progress_callback=progress_callback)
    
    print("Начиная парсинг первых 5 страниц myauto.ge...")
    parser.parse_all_pages(max_pages=5)
    
    print(f"\nВсего загружено: {len(parser.all_listings)} объявлений")
    
    if parser.all_listings:
        output_file = parser.save_to_file()
        print(f"Сохранено в: {output_file}")
