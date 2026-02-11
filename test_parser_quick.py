#!/usr/bin/env python
"""Quick test of updated parser."""

from mileon_saas.services.full_site_parser import FullSiteParser

print("Testing updated parser...")
parser = FullSiteParser(delay_seconds=1.0)

print("Parsing first page...")
parser.parse_all_pages(max_pages=1)

print(f"Success! Loaded {len(parser.all_listings)} listings")

if parser.all_listings:
    print("\nFirst 5 listings:")
    for car in parser.all_listings[:5]:
        print(f"  - {car.get('make_name')} {car.get('model', 'N/A')} ({car.get('year')}) - ${car.get('price_usd')}")
    
    # Save
    output = parser.save_to_file()
    print(f"\nSaved to: {output}")
else:
    print("ERROR: No listings loaded!")
