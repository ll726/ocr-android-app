from simple_price_checker import get_simple_prices

print("Simple Price Test")
items = get_simple_prices("test", 3)
print(f"Found {len(items)} items")

for i, item in enumerate(items, 1):
    print(f"{i}. {item['title']} - {item['price']} yen ({item['source']})")