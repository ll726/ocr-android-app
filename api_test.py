# -*- coding: utf-8 -*-
import sys
import requests
import json
from real_ai_summary_helper import RealAISummaryHelper

def test_internet():
    """インターネット接続テスト"""
    try:
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_gemini_api():
    """Gemini API接続テスト"""
    helper = RealAISummaryHelper()
    
    if not helper.config['gemini']['enabled']:
        return False, "Gemini APIが有効化されていません"
    
    api_key = helper.config['gemini']['api_key']
    if not api_key:
        return False, "APIキーが設定されていません"
    
    # 簡単なテストリクエスト
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        
        data = {
            'contents': [
                {
                    'parts': [
                        {'text': 'Hello'}
                    ]
                }
            ]
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, "接続成功！"
        elif response.status_code == 400:
            return False, "APIキーまたはリクエスト形式が無効です"
        elif response.status_code == 403:
            return False, "API権限がありません（APIキーを確認）"
        elif response.status_code == 429:
            return False, "レート制限に達しました（しばらく待ってから再試行）"
        else:
            return False, f"HTTPエラー: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "タイムアウト（ネットワーク接続を確認）"
    except requests.exceptions.ConnectionError:
        return False, "接続エラー（インターネット接続を確認）"
    except Exception as e:
        return False, f"予期しないエラー: {e}"

def main():
    print("=== API接続診断 ===")
    
    # インターネット接続テスト
    print("1. インターネット接続テスト...")
    if test_internet():
        print("✅ インターネット接続: OK")
    else:
        print("❌ インターネット接続: 失敗")
        print("   WiFi/有線接続を確認してください")
        return
    
    # Gemini API テスト
    print("\n2. Gemini API接続テスト...")
    success, message = test_gemini_api()
    
    if success:
        print("✅ Gemini API: " + message)
        print("\n🎉 全て正常です！Iキーを使用できます。")
    else:
        print("❌ Gemini API: " + message)
        print("\n🔧 解決方法:")
        
        if "APIキー" in message:
            print("   1. AI要約セットアップ.batを再実行")
            print("   2. https://makersuite.google.com/app/apikey で新しいキーを取得")
        elif "権限" in message:
            print("   1. Google AI StudioでGemini APIが有効か確認")
            print("   2. プロジェクトでGemini APIが許可されているか確認")
        elif "レート制限" in message:
            print("   1. 1-2分待ってから再試行")
            print("   2. リクエスト頻度を下げる")
        else:
            print("   1. ネットワーク設定を確認")
            print("   2. ファイアウォール設定を確認")

if __name__ == "__main__":
    main()
    print("\n" + "="*30)
    input("Enterキーで終了...")