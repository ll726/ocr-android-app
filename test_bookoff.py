from bookoff_scraper import get_bookoff_prices

print("BookOff Price Test")
items = get_bookoff_prices("test", 3)
print(f"Found {len(items)} items")

for i, item in enumerate(items, 1):
    print(f"{i}. {item['title']} - {item['price']} yen ({item['source']})")