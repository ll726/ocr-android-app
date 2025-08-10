from rakuma_scraper import get_rakuma_prices

print("Rakuma SOLD Price Test")
items = get_rakuma_prices("iPhone", 3)
print(f"Found {len(items)} items")

for i, item in enumerate(items, 1):
    print(f"{i}. {item['title']} - {item['price']} yen ({item['source']})")
    print(f"   Condition: {item['condition']}")
    print(f"   Shop: {item['shop']}")
    print()