import requests
import json
from googletrans import Translator
import time
from datetime import datetime
import re

class TranslationHelper:
    """
    OCR結果翻訳ヘルパークラス
    複数の翻訳サービスに対応
    """
    
    def __init__(self):
        self.google_translator = None
        self.supported_languages = {
            'ja': '日本語',
            'en': '英語',
            'ko': '韓国語',
            'zh': '中国語（簡体字）',
            'zh-tw': '中国語（繁体字）',
            'es': 'スペイン語',
            'fr': 'フランス語',
            'de': 'ドイツ語',
            'it': 'イタリア語',
            'pt': 'ポルトガル語',
            'ru': 'ロシア語',
            'ar': 'アラビア語',
            'th': 'タイ語',
            'vi': 'ベトナム語'
        }
        self._initialize_google_translator()
    
    def _initialize_google_translator(self):
        """Google翻訳を初期化"""
        try:
            self.google_translator = Translator()
            print("[OK] Google翻訳エンジンを初期化しました")
        except Exception as e:
            print(f"Google翻訳初期化エラー: {e}")
            self.google_translator = None
    
    def translate_text(self, text, target_lang='en', source_lang='auto'):
        """
        テキストを翻訳
        
        Args:
            text (str): 翻訳するテキスト
            target_lang (str): 翻訳先言語コード
            source_lang (str): 翻訳元言語コード ('auto' で自動検出)
            
        Returns:
            dict: 翻訳結果情報
        """
        if not text or text.strip() == "":
            return {"error": "翻訳するテキストが空です"}
        
        try:
            print(f"翻訳中: {text[:50]}...")
            print(f"翻訳方向: {source_lang} → {target_lang}")
            
            # Google翻訳で翻訳
            result = self.google_translator.translate(
                text, 
                dest=target_lang, 
                src=source_lang
            )
            
            translation_info = {
                'original_text': text,
                'translated_text': result.text,
                'source_language': result.src,
                'source_language_name': self.supported_languages.get(result.src, result.src),
                'target_language': target_lang,
                'target_language_name': self.supported_languages.get(target_lang, target_lang),
                'confidence': getattr(result, 'confidence', None),
                'service': 'Google Translate',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"[OK] 翻訳完了: {result.text[:50]}...")
            return translation_info
            
        except Exception as e:
            print(f"Google翻訳エラー: {e}")
            return self._fallback_translate(text, target_lang, source_lang)
    
    def _fallback_translate(self, text, target_lang, source_lang):
        """翻訳失敗時のフォールバック処理"""
        print("フォールバック翻訳を実行中...")
        
        # シンプルな辞書ベース翻訳（日→英のみ）
        if source_lang == 'ja' and target_lang == 'en':
            simple_translations = {
                'こんにちは': 'Hello',
                'ありがとう': 'Thank you',
                'さようなら': 'Goodbye',
                'おはよう': 'Good morning',
                'こんばんは': 'Good evening',
                '名前': 'Name',
                '住所': 'Address',
                '電話番号': 'Phone number',
                'メール': 'Email',
                '会社': 'Company',
                '価格': 'Price',
                '商品': 'Product',
                '注文': 'Order',
                '配送': 'Delivery',
                '支払い': 'Payment'
            }
            
            translated_parts = []
            words = text.split()
            
            for word in words:
                if word in simple_translations:
                    translated_parts.append(simple_translations[word])
                else:
                    translated_parts.append(f"[{word}]")  # 翻訳できない部分は括弧で囲む
            
            fallback_result = ' '.join(translated_parts)
            
            return {
                'original_text': text,
                'translated_text': fallback_result,
                'source_language': 'ja',
                'source_language_name': '日本語',
                'target_language': target_lang,
                'target_language_name': self.supported_languages.get(target_lang, target_lang),
                'confidence': None,
                'service': 'Simple Dictionary (Fallback)',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return {"error": f"翻訳に失敗しました: {text[:30]}..."}
    
    def detect_language(self, text):
        """言語を自動検出"""
        if not self.google_translator:
            return None
        
        try:
            detection = self.google_translator.detect(text)
            return {
                'language': detection.lang,
                'language_name': self.supported_languages.get(detection.lang, detection.lang),
                'confidence': detection.confidence
            }
        except Exception as e:
            print(f"言語検出エラー: {e}")
            return None
    
    def batch_translate(self, texts, target_lang='en', source_lang='auto'):
        """複数のテキストを一括翻訳"""
        results = []
        
        for i, text in enumerate(texts):
            print(f"翻訳中 ({i+1}/{len(texts)}): {text[:30]}...")
            result = self.translate_text(text, target_lang, source_lang)
            results.append(result)
            
            # API制限を避けるため少し待機
            time.sleep(0.5)
        
        return results
    
    def get_popular_languages(self):
        """よく使われる言語のリストを取得"""
        popular = {
            'en': '英語',
            'ja': '日本語', 
            'ko': '韓国語',
            'zh': '中国語',
            'es': 'スペイン語',
            'fr': 'フランス語',
            'de': 'ドイツ語'
        }
        return popular

class OfflineTranslationHelper:
    """
    オフライン翻訳ヘルパー（簡易版）
    インターネット接続不要の基本的な翻訳
    """
    
    def __init__(self):
        self.ja_to_en_dict = {
            # 基本的な挨拶
            'こんにちは': 'Hello',
            'おはよう': 'Good morning',
            'こんばんは': 'Good evening',
            'さようなら': 'Goodbye',
            'ありがとう': 'Thank you',
            'すみません': 'Excuse me',
            'はい': 'Yes',
            'いいえ': 'No',
            
            # 基本的な単語
            '名前': 'Name',
            '住所': 'Address', 
            '電話': 'Phone',
            'メール': 'Email',
            '会社': 'Company',
            '学校': 'School',
            '家': 'House',
            '車': 'Car',
            
            # 商品・買い物関連
            '価格': 'Price',
            '商品': 'Product',
            '店': 'Shop',
            '買い物': 'Shopping',
            '注文': 'Order',
            '支払い': 'Payment',
            'レシート': 'Receipt',
            
            # 数字
            '一': 'One',
            '二': 'Two', 
            '三': 'Three',
            '四': 'Four',
            '五': 'Five',
            '六': 'Six',
            '七': 'Seven',
            '八': 'Eight',
            '九': 'Nine',
            '十': 'Ten',
            
            # 日付・時間
            '今日': 'Today',
            '明日': 'Tomorrow',
            '昨日': 'Yesterday',
            '時間': 'Time',
            '日': 'Day',
            '月': 'Month',
            '年': 'Year'
        }
    
    def translate_japanese_to_english(self, text):
        """日本語から英語への簡易翻訳"""
        if not text:
            return None
        
        translated_words = []
        
        # 単語単位で翻訳
        for word in text:
            if word in self.ja_to_en_dict:
                translated_words.append(self.ja_to_en_dict[word])
            elif word.isspace():
                translated_words.append(word)
            else:
                # 翻訳できない文字はそのまま
                translated_words.append(word)
        
        translated_text = ''.join(translated_words)
        
        return {
            'original_text': text,
            'translated_text': translated_text,
            'source_language': 'ja',
            'target_language': 'en',
            'service': 'Offline Dictionary',
            'note': 'オフライン簡易翻訳'
        }

def format_translation_result(translation_result):
    """翻訳結果を見やすい形式でフォーマット"""
    if 'error' in translation_result:
        return f"翻訳エラー: {translation_result['error']}"
    
    result = f"""
=== 翻訳結果 ===
元のテキスト: {translation_result['original_text']}
翻訳結果: {translation_result['translated_text']}

言語情報:
  翻訳元: {translation_result.get('source_language_name', 'Unknown')} ({translation_result.get('source_language', '')})
  翻訳先: {translation_result.get('target_language_name', 'Unknown')} ({translation_result.get('target_language', '')})

翻訳サービス: {translation_result.get('service', 'Unknown')}
実行日時: {translation_result.get('timestamp', 'Unknown')}
==============
"""
    
    return result

def quick_translate(text, target_lang='en', source_lang='auto'):
    """テキストを素早く翻訳"""
    helper = TranslationHelper()
    result = helper.translate_text(text, target_lang, source_lang)
    return format_translation_result(result)

def show_supported_languages():
    """サポートされている言語一覧を表示"""
    helper = TranslationHelper()
    print("\n=== サポート言語一覧 ===")
    for code, name in helper.get_popular_languages().items():
        print(f"{code}: {name}")
    print("======================")

if __name__ == "__main__":
    # テスト実行
    print("翻訳機能のテスト")
    
    # 日本語から英語への翻訳テスト
    test_text_ja = "こんにちは、世界！これはOCRで読み取った文字の翻訳テストです。"
    print(f"\nテスト1: 日本語 → 英語")
    print(f"元のテキスト: {test_text_ja}")
    
    helper = TranslationHelper()
    result = helper.translate_text(test_text_ja, 'en', 'ja')
    print(format_translation_result(result))
    
    # 英語から日本語への翻訳テスト
    test_text_en = "Hello, world! This is a translation test of text read by OCR."
    print(f"\nテスト2: 英語 → 日本語")
    print(f"元のテキスト: {test_text_en}")
    
    result = helper.translate_text(test_text_en, 'ja', 'en')
    print(format_translation_result(result))
    
    # 言語検出テスト
    print(f"\nテスト3: 言語検出")
    detection = helper.detect_language("这是中文文本")
    print(f"検出結果: {detection}")
    
    # サポート言語表示
    show_supported_languages()