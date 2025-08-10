# -*- coding: utf-8 -*-
import requests
import json

def test_gemini_models():
    """利用可能なGeminiモデルを確認"""
    api_key = "AIzaSyAtzLXW2gvFcZ8w1UcQo5Uc8yOXY1VzVlU"
    
    # モデル一覧を取得
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("\n利用可能なモデル:")
            for model in models.get('models', []):
                model_name = model.get('name', 'Unknown')
                if 'gemini' in model_name.lower():
                    print(f"  - {model_name}")
        else:
            print(f"エラー: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"エラー: {e}")

def test_specific_model(model_name):
    """特定のモデルで要約テスト"""
    api_key = "AIzaSyAtzLXW2gvFcZ8w1UcQo5Uc8yOXY1VzVlU"
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
        
        data = {
            'contents': [
                {
                    'parts': [
                        {'text': 'こんにちは、テストです。'}
                    ]
                }
            ]
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"\nモデル {model_name} のテスト:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 成功！")
            return True
        else:
            print(f"❌ 失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == "__main__":
    print("=== Gemini API詳細テスト ===")
    
    # 1. モデル一覧取得
    test_gemini_models()
    
    # 2. 各モデルをテスト
    models_to_test = [
        'gemini-pro',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'models/gemini-pro',
        'models/gemini-1.5-flash'
    ]
    
    print("\n=== モデル別テスト ===")
    for model in models_to_test:
        if test_specific_model(model):
            print(f"✅ {model} が動作します！")
            break
    
    input("\nEnterで終了...")