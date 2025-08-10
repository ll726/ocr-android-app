from rakuten_api_client import get_rakuten_prices, analyze_rakuten_prices, format_rakuten_price_info

# テスト実行
test_keyword = "iPhone"
print(f"テストキーワード: {test_keyword}")

items = get_rakuten_prices(test_keyword, 3)
analysis = analyze_rakuten_prices(items)
result = format_rakuten_price_info(analysis)
print(result)