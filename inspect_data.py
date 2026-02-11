#!/usr/bin/env python
"""Analyze actual data structure from API."""

import json
from mileon_saas.services.full_site_parser import FullSiteParser

parser = FullSiteParser()
parser.parse_all_pages(max_pages=1)

if parser.all_listings:
    # Save first listing for inspection
    with open('first_listing.json', 'w', encoding='utf-8') as f:
        json.dump(parser.all_listings[0], f, ensure_ascii=False, indent=2)
    
    first = parser.all_listings[0]
    print("First listing structure:")
    print(json.dumps(first, indent=2, ensure_ascii=False)[:500])
    
    print("\n\nAvailable keys:")
    print(list(first.keys()))
    
    print(f"\n\nSample values:")
    for key in list(first.keys())[:10]:
        val = first[key]
        if isinstance(val, (str, int, float, bool, type(None))):
            print(f"  {key}: {val}")
        else:
            print(f"  {key}: {type(val).__name__}")
