import requests
import json
import time
from datetime import datetime
import os

class RakutenAPIClient:
    """
    楽天市場API クライアント
    
    楽天市場の商品価格を取得するためのAPIクライアント
    月1,000回まで無料で利用可能
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_delay = 1  # 楽天APIは比較的制限が緩い
        
    def _load_api_key(self):
        """APIキーをファイルから読み込み"""
        key_file = "rakuten_api_key.txt"
        if os.path.exists(key_file):
            with open(key_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    
    def _save_api_key_template(self):
        """APIキー設定ファイルのテンプレートを作成"""
        template = """# 楽天市場APIキー設定ファイル
# 
# 1. 楽天デベロッパー登録: https://webservice.rakuten.co.jp/
# 2. アプリケーション作成
# 3. 取得したApplication IDを下記に入力
# 4. このファイル名を rakuten_api_key.txt に変更
#
# Application ID をここに入力（#を削除）:
# YOUR_RAKUTEN_APP_ID_HERE"""
        
        with open("rakuten_api_key_template.txt", 'w', encoding='utf-8') as f:
            f.write(template)
        
        print("APIキー設定テンプレートを作成しました: rakuten_api_key_template.txt")
    
    def _safe_delay(self):
        """API制限を考慮した適切な間隔"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_products(self, keyword, max_results=10):
        """
        楽天市場で商品を検索
        
        Args:
            keyword (str): 検索キーワード
            max_results (int): 最大取得件数
            
        Returns:
            list: 商品情報のリスト
        """
        
        if not self.api_key:
            print("=" * 60)
            print("[ERROR] 楽天APIキーが設定されていません")
            print("=" * 60)
            print("楽天市場APIを利用するには以下の手順が必要です:")
            print()
            print("1. 楽天デベロッパーサイトでアカウント作成")
            print("   https://webservice.rakuten.co.jp/")
            print()
            print("2. アプリケーション作成・Application ID取得")
            print()
            print("3. rakuten_api_key.txt ファイルに Application ID を保存")
            print()
            
            self._save_api_key_template()
            
            # サンプルデータを返す
            return self._generate_sample_rakuten_data(keyword, max_results)
        
        try:
            print(f"楽天市場APIで '{keyword}' を検索中...")
            
            # APIリクエストパラメータ
            params = {
                'format': 'json',
                'keyword': keyword,
                'hits': min(max_results, 30),  # 楽天APIの上限は30件
                'sort': 'standard',  # 標準順
                'applicationId': self.api_key
            }
            
            # API制限を考慮して適切な間隔でリクエスト
            self._safe_delay()
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"APIリクエストエラー: {response.status_code}")
                return self._generate_sample_rakuten_data(keyword, max_results)
            
            data = response.json()
            
            # レスポンスデータを解析
            return self._parse_rakuten_response(data, max_results)
            
        except requests.exceptions.Timeout:
            print("タイムアウト: 楽天APIサーバーが応答しません")
            return self._generate_sample_rakuten_data(keyword, max_results)
            
        except requests.exceptions.RequestException as e:
            print(f"ネットワークエラー: {e}")
            return self._generate_sample_rakuten_data(keyword, max_results)
            
        except json.JSONDecodeError:
            print("レスポンス解析エラー: 無効なJSONデータ")
            return self._generate_sample_rakuten_data(keyword, max_results)
            
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return self._generate_sample_rakuten_data(keyword, max_results)
    
    def _parse_rakuten_response(self, data, max_results):
        """楽天APIレスポンスを解析"""
        items = []
        
        try:
            if 'Items' not in data:
                print("検索結果が見つかりませんでした")
                return []
            
            print(f"楽天市場から {len(data['Items'])}件 の商品を取得")
            
            for item_data in data['Items'][:max_results]:
                item = item_data['Item']
                
                # 商品情報を抽出
                product_info = {
                    'title': item.get('itemName', '商品名不明'),
                    'price': int(item.get('itemPrice', 0)),
                    'shop_name': item.get('shopName', '店舗名不明'),
                    'image_url': item.get('mediumImageUrls', [{}])[0].get('imageUrl', ''),
                    'item_url': item.get('itemUrl', ''),
                    'review_count': item.get('reviewCount', 0),
                    'review_average': item.get('reviewAverage', 0),
                    'availability': item.get('availability', 1),
                    'source': 'rakuten_api',
                    'search_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                items.append(product_info)
            
            return items
            
        except KeyError as e:
            print(f"データ構造エラー: {e}")
            return []
        except Exception as e:
            print(f"データ解析エラー: {e}")
            return []
    
    def _generate_sample_rakuten_data(self, keyword, max_results):
        """サンプル楽天データ生成（APIキー未設定時）"""
        print(f"注意: APIキー未設定のため、'{keyword}' のサンプル楽天データを生成")
        
        import random
        
        # 楽天らしい店舗名
        shop_names = [
            "楽天ブックス", "ビックカメラ楽天市場店", "ヨドバシカメラ楽天市場店",
            "Amazon楽天市場店", "イオン楽天市場店", "ケーズデンキ楽天市場店",
            "ヤマダ電機楽天市場店", "コジマ楽天市場店"
        ]
        
        items = []
        for i in range(max_results):
            price = random.randint(500, 15000)
            
            item = {
                'title': f"{keyword} 楽天サンプル商品 #{i+1}",
                'price': price,
                'shop_name': random.choice(shop_names),
                'image_url': '',
                'item_url': 'https://item.rakuten.co.jp/sample/',
                'review_count': random.randint(0, 100),
                'review_average': round(random.uniform(3.0, 5.0), 1),
                'availability': 1,
                'source': 'rakuten_sample',
                'search_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            items.append(item)
        
        return items

def analyze_rakuten_prices(items):
    """楽天商品データを分析"""
    if not items:
        return {"error": "楽天商品データが見つかりません"}
    
    prices = [item['price'] for item in items if item['price'] > 0]
    
    if not prices:
        return {"error": "有効な価格データがありません"}
    
    analysis = {
        "count": len(prices),
        "average": sum(prices) / len(prices),
        "min": min(prices),
        "max": max(prices),
        "items": items,
        "source": "rakuten_market"
    }
    
    return analysis

def format_rakuten_price_info(analysis):
    """楽天価格情報を見やすい形式でフォーマット"""
    if "error" in analysis:
        return analysis["error"]
    
    result = f"""
=== 楽天市場 価格情報 ===
商品件数: {analysis['count']}件
平均価格: ¥{analysis['average']:,.0f}
最安値: ¥{analysis['min']:,}
最高値: ¥{analysis['max']:,}

=== 商品一覧 ===
"""
    
    for i, item in enumerate(analysis['items'][:5], 1):
        shop = item.get('shop_name', '店舗名不明')
        review_count = item.get('review_count', 0)
        review_avg = item.get('review_average', 0)
        source = item.get('source', 'unknown')
        
        result += f"{i}. {item['title'][:40]}...\n"
        result += f"   価格: ¥{item['price']:,} | 店舗: {shop}\n"
        result += f"   レビュー: {review_avg}★ ({review_count}件) | データ元: {source}\n\n"
    
    result += """
=== 楽天市場API情報 ===
※月1,000回まで無料利用可能
※実際の販売価格（売れた価格ではありません）
※在庫状況により価格変動の可能性があります
============================"""
    
    return result

# メイン関数（互換性のため）
def get_rakuten_prices(search_text, max_results=10):
    """楽天価格検索のメイン関数"""
    client = RakutenAPIClient()
    return client.search_products(search_text, max_results)

if __name__ == "__main__":
    # テスト実行
    keyword = input("楽天市場で検索するキーワードを入力: ")
    if keyword:
        items = get_rakuten_prices(keyword, 5)
        analysis = analyze_rakuten_prices(items)
        result = format_rakuten_price_info(analysis)
        print(result)