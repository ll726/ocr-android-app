# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from rakuten_api_client import get_rakuten_prices

print("Testing Rakuten API...")
items = get_rakuten_prices("test", 2)
print(f"Got {len(items)} items")
if items:
    print(f"First item: {items[0]['title']} - {items[0]['price']} yen")