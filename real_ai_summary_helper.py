# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from datetime import datetime
import time

class RealAISummaryHelper:
    """
    真のAI API要約ヘルパークラス
    OpenAI GPT、Google Gemini、Claude APIに対応
    """
    
    def __init__(self):
        # API設定ファイル
        self.config_file = "ai_api_config.json"
        self.load_api_config()
        
        # 各AIの要約プロンプト
        self.summary_prompts = {
            'short': """以下の文章を3行以内で要約してください。重要なポイントのみを簡潔に：

{text}

要約:""",
            
            'detailed': """以下の文章を詳細に分析し、構造化して要約してください：

{text}

以下の形式で要約してください：
【主要内容】
【重要なポイント】
【結論・今後の方針】
【関係者・数値情報】""",
            
            'business': """以下のビジネス文書を分析し、意思決定に必要な情報を要約してください：

{text}

以下の観点から要約してください：
- 現状の問題・課題
- 提案・解決策
- 期待される効果・結果
- 必要なアクション・スケジュール""",
            
            'bullet': """以下の文章を読みやすい箇条書き形式で要約してください：

{text}

要約（箇条書き）:"""
        }
    
    def load_api_config(self):
        """API設定を読み込み"""
        default_config = {
            "openai": {
                "api_key": "",
                "model": "gpt-3.5-turbo",
                "enabled": False
            },
            "gemini": {
                "api_key": "",
                "model": "gemini-1.5-flash",
                "enabled": False
            },
            "claude": {
                "api_key": "",
                "model": "claude-3-haiku-20240307",
                "enabled": False
            },
            "preferred_api": "openai"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # デフォルト設定とマージ
                for api in default_config:
                    if api not in self.config:
                        self.config[api] = default_config[api]
            else:
                self.config = default_config
                self.save_api_config()
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            self.config = default_config
    
    def save_api_config(self):
        """API設定を保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
    
    def setup_wizard(self):
        """API設定ウィザード"""
        print("🤖 真のAI要約機能セットアップ")
        print("="*50)
        
        print("\n利用したいAI APIを選択してください（複数選択可）：")
        print("1. OpenAI GPT (推奨) - 高品質、安定")
        print("2. Google Gemini - 無料枠大、多言語")
        print("3. Anthropic Claude - 長文対応、高精度")
        print("0. スキップ")
        
        choice = input("\n選択 (1,2,3,0): ").strip()
        
        if choice == "0":
            return False
        
        if "1" in choice:
            self.setup_openai()
        if "2" in choice:
            self.setup_gemini()
        if "3" in choice:
            self.setup_claude()
        
        # 優先APIの選択
        enabled_apis = [api for api in ['openai', 'gemini', 'claude'] 
                       if self.config[api]['enabled']]
        
        if enabled_apis:
            print(f"\n設定されたAPI: {', '.join(enabled_apis)}")
            if len(enabled_apis) > 1:
                preferred = input(f"優先API ({'/'.join(enabled_apis)}): ").strip()
                if preferred in enabled_apis:
                    self.config['preferred_api'] = preferred
            else:
                self.config['preferred_api'] = enabled_apis[0]
        
        self.save_api_config()
        return len(enabled_apis) > 0
    
    def setup_openai(self):
        """OpenAI API設定"""
        print("\n🔧 OpenAI API設定")
        print("APIキーの取得: https://platform.openai.com/api-keys")
        api_key = input("OpenAI APIキー: ").strip()
        
        if api_key:
            self.config['openai']['api_key'] = api_key
            self.config['openai']['enabled'] = True
            print("✅ OpenAI API設定完了")
    
    def setup_gemini(self):
        """Google Gemini API設定"""
        print("\n🔧 Google Gemini API設定")
        print("APIキーの取得: https://makersuite.google.com/app/apikey")
        api_key = input("Gemini APIキー: ").strip()
        
        if api_key:
            self.config['gemini']['api_key'] = api_key
            self.config['gemini']['enabled'] = True
            print("✅ Gemini API設定完了")
    
    def setup_claude(self):
        """Claude API設定"""
        print("\n🔧 Claude API設定")
        print("APIキーの取得: https://console.anthropic.com/")
        api_key = input("Claude APIキー: ").strip()
        
        if api_key:
            self.config['claude']['api_key'] = api_key
            self.config['claude']['enabled'] = True
            print("✅ Claude API設定完了")
    
    def call_openai_api(self, prompt, text):
        """OpenAI API呼び出し"""
        if not self.config['openai']['enabled'] or not self.config['openai']['api_key']:
            return None, "OpenAI APIが設定されていません"
        
        try:
            headers = {
                'Authorization': f"Bearer {self.config['openai']['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.config['openai']['model'],
                'messages': [
                    {'role': 'user', 'content': prompt.format(text=text)}
                ],
                'max_tokens': 500,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip(), None
            else:
                return None, f"OpenAI APIエラー: {response.status_code}"
                
        except Exception as e:
            return None, f"OpenAI API呼び出しエラー: {e}"
    
    def call_gemini_api(self, prompt, text):
        """Google Gemini API呼び出し"""
        if not self.config['gemini']['enabled'] or not self.config['gemini']['api_key']:
            return None, "Gemini APIが設定されていません"
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/{self.config['gemini']['model']}:generateContent?key={self.config['gemini']['api_key']}"
            
            data = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt.format(text=text)}
                        ]
                    }
                ],
                'generationConfig': {
                    'maxOutputTokens': 500,
                    'temperature': 0.3
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return content.strip(), None
                else:
                    return None, "Gemini APIから結果を取得できませんでした"
            else:
                return None, f"Gemini APIエラー: {response.status_code}"
                
        except Exception as e:
            return None, f"Gemini API呼び出しエラー: {e}"
    
    def call_claude_api(self, prompt, text):
        """Claude API呼び出し"""
        if not self.config['claude']['enabled'] or not self.config['claude']['api_key']:
            return None, "Claude APIが設定されていません"
        
        try:
            headers = {
                'x-api-key': self.config['claude']['api_key'],
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': self.config['claude']['model'],
                'max_tokens': 500,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt.format(text=text)
                    }
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text'].strip(), None
            else:
                return None, f"Claude APIエラー: {response.status_code}"
                
        except Exception as e:
            return None, f"Claude API呼び出しエラー: {e}"
    
    def get_real_ai_summary(self, text, summary_type='short', preferred_api=None):
        """真のAI要約を取得"""
        if not text or len(text.strip()) < 10:
            return None, "テキストが短すぎます"
        
        # API選択
        api_to_use = preferred_api or self.config.get('preferred_api', 'openai')
        
        # プロンプト選択
        prompt = self.summary_prompts.get(summary_type, self.summary_prompts['short'])
        
        # API呼び出し
        if api_to_use == 'openai':
            result, error = self.call_openai_api(prompt, text)
            api_name = "OpenAI GPT"
        elif api_to_use == 'gemini':
            result, error = self.call_gemini_api(prompt, text)
            api_name = "Google Gemini"
        elif api_to_use == 'claude':
            result, error = self.call_claude_api(prompt, text)
            api_name = "Anthropic Claude"
        else:
            return None, f"未知のAPI: {api_to_use}"
        
        if result:
            return {
                'summary': result,
                'api_used': api_name,
                'model': self.config[api_to_use]['model'],
                'type': summary_type
            }, None
        else:
            # フォールバック: 他のAPIを試行
            fallback_apis = [api for api in ['openai', 'gemini', 'claude'] 
                           if api != api_to_use and self.config[api]['enabled']]
            
            for fallback_api in fallback_apis:
                print(f"🔄 {fallback_api}にフォールバック中...")
                if fallback_api == 'openai':
                    result, error = self.call_openai_api(prompt, text)
                elif fallback_api == 'gemini':
                    result, error = self.call_gemini_api(prompt, text)
                elif fallback_api == 'claude':
                    result, error = self.call_claude_api(prompt, text)
                
                if result:
                    return {
                        'summary': result,
                        'api_used': fallback_api.title(),
                        'model': self.config[fallback_api]['model'],
                        'type': summary_type
                    }, None
            
            return None, f"全てのAPIで失敗: {error}"
    
    def is_configured(self):
        """APIが設定されているかチェック"""
        return any(self.config[api]['enabled'] for api in ['openai', 'gemini', 'claude'])

def format_real_ai_summary_result(summary_data, original_length):
    """真AI要約結果をフォーマット"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted = f"""
{'='*50}
🧠 真のAI要約結果 - {timestamp}
{'='*50}

🤖 AI情報:
- 使用AI: {summary_data['api_used']}
- モデル: {summary_data['model']}
- 要約タイプ: {summary_data['type']}

📊 テキスト情報:
- 元テキスト長: {original_length}文字
- AI要約後: {len(summary_data['summary'])}文字
- 圧縮率: {100*(1-len(summary_data['summary'])/max(original_length, 1)):.1f}%

🧠 AI要約内容:
{summary_data['summary']}

{'='*50}
"""
    
    return formatted

# テスト・セットアップ用
if __name__ == "__main__":
    helper = RealAISummaryHelper()
    
    if not helper.is_configured():
        print("AI APIの設定が必要です。")
        if helper.setup_wizard():
            print("\n✅ セットアップ完了！")
        else:
            print("\n❌ セットアップをスキップしました。")
    else:
        # テスト実行
        test_text = """
        当社の業績が大幅に改善しました。売上は前年比20%増加し、
        利益率も向上しています。新商品の好調な売れ行きが主な要因です。
        来四半期はさらなる成長が期待されます。
        """
        
        print("\n=== 真のAI要約テスト ===")
        result, error = helper.get_real_ai_summary(test_text, 'short')
        
        if result:
            print(format_real_ai_summary_result(result, len(test_text)))
        else:
            print(f"エラー: {error}")