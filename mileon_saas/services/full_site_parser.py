#!/usr/bin/env python
"""Full myauto.ge site parser with progress tracking and delay support."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import cloudscraper
from fake_useragent import UserAgent


# Mapping of car manufacturer IDs to names (from parser.py)
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
    786: 'Alfa Romeo',
    987: 'Can-Am',
}


class FullSiteParser:
    """Parse all listings from myauto.ge with progress tracking and deduplication."""
    
    def __init__(self, delay_seconds: float = 2.0, progress_callback: Optional[Callable] = None):
        """
        Initialize parser.
        
        Args:
            delay_seconds: Pause between requests to avoid blocking
            progress_callback: Function to call with (current, total, elapsed_time) for progress updates
        """
        self.delay_seconds = delay_seconds
        self.progress_callback = progress_callback
        self.scraper = cloudscraper.create_scraper()
        self.ua = UserAgent()
        self.base_url = "https://api2.myauto.ge/en/products"
        self.all_listings = []
        self.start_time = None
        self.existing_car_ids = set()  # Track existing car IDs for deduplication
        self.new_listings_count = 0    # Count of new listings added
        
        self._setup_session()
    
    def _setup_session(self):
        """Configure scraper session."""
        self.scraper.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def _update_progress(self):
        """Call progress callback if provided."""
        if self.progress_callback and self.start_time:
            elapsed = time.time() - self.start_time
            self.progress_callback(self.new_listings_count, elapsed)
    
    def _load_existing_data(self):
        """Load existing car IDs from the merged JSON file (fallback to legacy files)."""
        self.existing_car_ids = set()

        merged_path = Path("full_site_merged.json")
        legacy_files = list(Path(".").glob("full_site_*.json"))
        files_to_read = [merged_path] if merged_path.exists() else legacy_files

        for json_file in files_to_read:
            try:
                with open(json_file, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                car_id = item.get("car_id")
                                if car_id:
                                    self.existing_car_ids.add(car_id)
            except Exception as exc:
                print(f"Warning: Could not read {json_file}: {exc}")

        if self.existing_car_ids:
            print(f"Loaded {len(self.existing_car_ids)} existing car IDs from previous saves")
    
    def _transform_listing(self, api_item: dict) -> dict:
        """Transform API response format to cars_data.json format."""
        make_id = api_item.get('man_id')
        make_name = MAKE_NAMES.get(make_id, f'Unknown ({make_id})')
        
        return {
            "date": api_item.get('order_date', ''),
            "phone": api_item.get('client_phone', ''),
            "year": api_item.get('prod_year'),
            "engine_volume": api_item.get('engine_volume'),
            "price_usd": api_item.get('price_usd'),
            "location": api_item.get('location_id'),
            "model_id": api_item.get('model_id'),
            "model": api_item.get('car_model', ''),
            "trim": '',
            "photo_url": f"https://static.my.ge/myauto/photos/{api_item.get('photo', '')}/thumbs/{api_item.get('car_id')}_1.jpg" if api_item.get('photo') else '',
            "description": api_item.get('car_desc', ''),
            "car_id": api_item.get('car_id'),
            "make": api_item.get('man_id'),
            "make_name": make_name,
            "fuel_type": api_item.get('fuel_type_id'),
            "category": api_item.get('category_id'),
            "rating": 0.0,
        }
    
    def _transform_listing(self, api_item: dict) -> dict:
        """Transform API response format to cars_data.json format."""
        make_id = api_item.get('man_id')
        make_name = MAKE_NAMES.get(make_id, f'Unknown ({make_id})')
        
        return {
            "date": api_item.get('order_date', ''),
            "phone": api_item.get('client_phone', ''),
            "year": api_item.get('prod_year'),
            "engine_volume": api_item.get('engine_volume'),
            "price_usd": api_item.get('price_usd'),
            "location": api_item.get('location_id'),
            "model_id": api_item.get('model_id'),
            "model": api_item.get('car_model', ''),
            "trim": '',
            "photo_url": f"https://static.my.ge/myauto/photos/{api_item.get('photo', '')}/thumbs/{api_item.get('car_id')}_1.jpg" if api_item.get('photo') else '',
            "description": api_item.get('car_desc', ''),
            "car_id": api_item.get('car_id'),
            "make": api_item.get('man_id'),
            "make_name": make_name,
            "fuel_type": api_item.get('fuel_type_id'),
            "category": api_item.get('category_id'),
            "rating": 0.0,
        }
    
    def parse_all_pages(self, max_pages: Optional[int] = None, skip_existing: bool = True) -> list[dict]:
        """
        Parse all pages from myauto.ge.
        
        Args:
            max_pages: Maximum pages to fetch (None for all pages)
            skip_existing: If True, skip listings that were already saved previously
        
        Returns:
            List of all new listings
        """
        self.all_listings = []
        self.new_listings_count = 0
        self.start_time = time.time()
        
        # Load existing data if deduplication is enabled
        if skip_existing:
            self._load_existing_data()
        
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
            
            try:
                # Fetch page
                params = {
                    'vehicleType': 0,
                    'ForRent': '',
                    'Mans': '',
                    'PriceFrom': 600,
                    'PriceTo': 50000,
                    'CurrencyID': 1,
                    'MileageType': 1,
                    'Customs': 1,
                    'Page': page,
                }
                
                response = self.scraper.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                # Handle new API response format
                items = []
                if isinstance(data, dict):
                    # New format: {data: {items: [], meta: {}}, ...}
                    if 'data' in data and isinstance(data['data'], dict):
                        items = data['data'].get('items', [])
                    # Or items directly in data
                    elif 'items' in data:
                        items = data['items']
                elif isinstance(data, list):
                    # Old format: direct array
                    items = data
                
                if not items:
                    break
                
                # Transform items to standard format and add to collection
                for item in items:
                    car_id = item.get('car_id')
                    
                    # Skip if already exists
                    if skip_existing and car_id in self.existing_car_ids:
                        continue
                    
                    transformed = self._transform_listing(item)
                    self.all_listings.append(transformed)
                    self.existing_car_ids.add(car_id)
                    self.new_listings_count += 1
                
                self._update_progress()
                
                # Check if this is last page (less than 20 items)
                if len(items) < 20:
                    break
                
                page += 1
                time.sleep(self.delay_seconds)  # Delay to avoid blocking
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        return self.all_listings
    
    def save_to_file(self, output_file: str = None) -> str:
        """
        Save parsed listings to JSON file.
        
        Args:
            output_file: Path to output file (defaults to full_site_YYYY_MM_DD_HH_MM_SS.json)
        
        Returns:
            Path to saved file
        """
        if not output_file:
            output_file = "full_site_merged.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        existing_items = []
        if output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    if isinstance(data, list):
                        existing_items = [item for item in data if isinstance(item, dict)]
            except Exception as exc:
                print(f"Warning: Could not read {output_path}: {exc}")

        def entry_score(item: dict) -> int:
            return sum(1 for value in item.values() if value not in (None, "", [], {}))

        merged_by_id = {}
        for item in existing_items:
            car_id = item.get("car_id")
            if car_id is not None:
                merged_by_id[car_id] = item

        for item in self.all_listings:
            car_id = item.get("car_id")
            if car_id is None:
                continue
            if car_id in merged_by_id:
                current = merged_by_id[car_id]
                if entry_score(item) > entry_score(current):
                    merged_by_id[car_id] = item
            else:
                merged_by_id[car_id] = item

        merged_items = list(merged_by_id.values())

        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(merged_items, handle, ensure_ascii=False, indent=2)

        return str(output_path)
