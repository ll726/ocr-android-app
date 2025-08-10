import os
import tempfile
from pathlib import Path
import subprocess
import json
import hashlib

class VoiceSynthesisHelper:
    """
    用意した音声から新しい読み上げ音声を生成するヘルパー
    複数の手法をサポート
    """
    
    def __init__(self, base_voice_folder="base_voices"):
        self.base_voice_folder = base_voice_folder
        self.generated_folder = "generated_voices"
        self.voice_models = {}
        
        os.makedirs(self.base_voice_folder, exist_ok=True)
        os.makedirs(self.generated_folder, exist_ok=True)
        
        self._load_voice_models()
    
    def _load_voice_models(self):
        """音声モデル情報を読み込み"""
        model_file = os.path.join(self.base_voice_folder, "voice_models.json")
        if os.path.exists(model_file):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    self.voice_models = json.load(f)
            except Exception as e:
                print(f"音声モデル読み込みエラー: {e}")
                self.voice_models = {}
    
    def register_voice_sample(self, speaker_name, sample_file_path, description=""):
        """
        音声サンプルを登録
        
        Args:
            speaker_name (str): 話者名
            sample_file_path (str): サンプル音声ファイルパス
            description (str): 音声の説明
        """
        if not os.path.exists(sample_file_path):
            print(f"[ERROR] サンプルファイルが見つかりません: {sample_file_path}")
            return False
        
        try:
            # サンプルファイルをコピー
            import shutil
            sample_filename = f"{speaker_name}_sample.wav"
            dest_path = os.path.join(self.base_voice_folder, sample_filename)
            shutil.copy2(sample_file_path, dest_path)
            
            # モデル情報を保存
            self.voice_models[speaker_name] = {
                "sample_file": sample_filename,
                "description": description,
                "created_at": str(datetime.now())
            }
            
            self._save_voice_models()
            print(f"[OK] 音声サンプルを登録: {speaker_name}")
            return True
            
        except Exception as e:
            print(f"音声サンプル登録エラー: {e}")
            return False
    
    def _save_voice_models(self):
        """音声モデル情報を保存"""
        model_file = os.path.join(self.base_voice_folder, "voice_models.json")
        try:
            from datetime import datetime
            with open(model_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_models, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"音声モデル保存エラー: {e}")
    
    def generate_speech_espeak(self, text, speaker_name=None, output_file=None):
        """
        eSpeak を使用した音声合成
        軽量で多言語対応
        """
        try:
            if output_file is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_file = os.path.join(self.generated_folder, f"espeak_{text_hash}.wav")
            
            # eSpeak コマンド実行
            cmd = [
                "espeak",
                "-v", "ja",  # 日本語
                "-s", "150",  # 速度
                "-w", output_file,  # 出力ファイル
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_file):
                print(f"[OK] eSpeak音声生成完了: {output_file}")
                return output_file
            else:
                print(f"[ERROR] eSpeak実行エラー: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("[WARNING] eSpeakがインストールされていません")
            return None
        except Exception as e:
            print(f"eSpeak音声生成エラー: {e}")
            return None
    
    def generate_speech_pyttsx3(self, text, speaker_name=None, output_file=None):
        """
        pyttsx3 を使用した音声合成（標準機能）
        """
        try:
            import pyttsx3
            
            if output_file is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_file = os.path.join(self.generated_folder, f"pyttsx3_{text_hash}.wav")
            
            engine = pyttsx3.init()
            
            # 音声設定
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'japanese' in voice.name.lower() or 'japan' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            # ファイルに保存
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            
            if os.path.exists(output_file):
                print(f"[OK] pyttsx3音声生成完了: {output_file}")
                return output_file
            else:
                print("[ERROR] pyttsx3音声ファイル生成失敗")
                return None
                
        except Exception as e:
            print(f"pyttsx3音声生成エラー: {e}")
            return None
    
    def generate_speech_windows_sapi(self, text, speaker_name=None, output_file=None):
        """
        Windows SAPI を使用した音声合成
        """
        try:
            import win32com.client
            
            if output_file is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_file = os.path.join(self.generated_folder, f"sapi_{text_hash}.wav")
            
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            
            # 音声ファイルに保存
            file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
            file_stream.Open(output_file, 3)  # 3 = write mode
            sapi.AudioOutputStream = file_stream
            
            sapi.Speak(text)
            
            file_stream.Close()
            
            if os.path.exists(output_file):
                print(f"[OK] Windows SAPI音声生成完了: {output_file}")
                return output_file
            else:
                print("[ERROR] Windows SAPI音声ファイル生成失敗")
                return None
                
        except Exception as e:
            print(f"Windows SAPI音声生成エラー: {e}")
            return None
    
    def generate_speech_coqui_tts(self, text, speaker_name=None, output_file=None):
        """
        Coqui TTS を使用した高品質音声合成
        （要インストール: pip install coqui-tts）
        """
        try:
            from TTS.api import TTS
            
            if output_file is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_file = os.path.join(self.generated_folder, f"coqui_{text_hash}.wav")
            
            # Coqui TTS初期化（日本語モデル）
            tts = TTS(model_name="tts_models/ja/kokoro/tacotron2-DDC")
            
            # 音声生成
            tts.tts_to_file(text=text, file_path=output_file)
            
            if os.path.exists(output_file):
                print(f"[OK] Coqui TTS音声生成完了: {output_file}")
                return output_file
            else:
                print("[ERROR] Coqui TTS音声ファイル生成失敗")
                return None
                
        except ImportError:
            print("[WARNING] Coqui TTSがインストールされていません")
            print("インストール方法: pip install coqui-tts")
            return None
        except Exception as e:
            print(f"Coqui TTS音声生成エラー: {e}")
            return None
    
    def generate_speech_auto(self, text, speaker_name=None, prefer_method="pyttsx3"):
        """
        利用可能な方法で自動的に音声生成
        
        Args:
            text (str): 音声化するテキスト
            speaker_name (str): 話者名（将来の拡張用）
            prefer_method (str): 優先する音声合成方法
        
        Returns:
            str: 生成された音声ファイルパス（失敗時はNone）
        """
        methods = {
            "pyttsx3": self.generate_speech_pyttsx3,
            "sapi": self.generate_speech_windows_sapi,
            "espeak": self.generate_speech_espeak,
            "coqui": self.generate_speech_coqui_tts
        }
        
        # 優先方法を最初に試す
        if prefer_method in methods:
            result = methods[prefer_method](text, speaker_name)
            if result:
                return result
        
        # 他の方法を順次試す
        for method_name, method_func in methods.items():
            if method_name != prefer_method:
                print(f"[INFO] {method_name} で音声生成を試行...")
                result = method_func(text, speaker_name)
                if result:
                    return result
        
        print("[ERROR] すべての音声生成方法が失敗しました")
        return None
    
    def batch_generate_common_words(self, word_list, speaker_name=None, method="auto"):
        """
        よく使用される単語をまとめて音声生成
        
        Args:
            word_list (list): 単語リスト
            speaker_name (str): 話者名
            method (str): 音声合成方法
        
        Returns:
            dict: {単語: 音声ファイルパス} の辞書
        """
        generated_files = {}
        
        print(f"[INFO] {len(word_list)}個の単語の音声を生成中...")
        
        for i, word in enumerate(word_list):
            print(f"[{i+1}/{len(word_list)}] 生成中: '{word}'")
            
            if method == "auto":
                audio_file = self.generate_speech_auto(word, speaker_name)
            else:
                method_func = getattr(self, f"generate_speech_{method}", None)
                if method_func:
                    audio_file = method_func(word, speaker_name)
                else:
                    print(f"[ERROR] 不明な音声合成方法: {method}")
                    audio_file = None
            
            if audio_file:
                generated_files[word] = audio_file
                print(f"[OK] '{word}' -> {audio_file}")
            else:
                print(f"[ERROR] '{word}' の音声生成に失敗")
        
        print(f"[完了] {len(generated_files)}/{len(word_list)}個の音声を生成しました")
        return generated_files
    
    def get_common_japanese_words(self):
        """よく使用される日本語単語リストを取得"""
        return [
            # 数字
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            "零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
            
            # 挨拶
            "こんにちは", "こんばんは", "おはようございます", 
            "ありがとうございます", "すみません", "失礼します",
            
            # よく読み取られる文字
            "円", "価格", "商品名", "商品", "値段", "料金", "税込", "税抜",
            "割引", "セール", "特価", "限定", "送料", "無料",
            
            # 単位
            "個", "本", "枚", "冊", "台", "点", "セット", "パック",
            
            # 時間・日付
            "時", "分", "秒", "日", "月", "年", "曜日", "今日", "明日", "昨日",
            
            # 場所
            "店", "店舗", "レジ", "会計", "お客様", "スタッフ"
        ]
    
    def create_setup_guide(self):
        """音声合成セットアップガイドを作成"""
        guide = f"""
=== 音声合成セットアップガイド ===

【基本的な使い方】
1. 音声合成方法を選択
2. よく読み取られる単語の音声を事前生成
3. OCRアプリで自動音声再生

【対応する音声合成方法】
✓ pyttsx3     - 標準（既にインストール済み）
✓ Windows SAPI - Windows標準の高品質音声
? eSpeak      - 軽量・多言語（要インストール）
? Coqui TTS   - 最高品質（要インストール）

【推奨セットアップ手順】
1. 共通単語の音声生成:
   helper = VoiceSynthesisHelper()
   words = helper.get_common_japanese_words()
   helper.batch_generate_common_words(words)

2. カスタム単語の追加:
   helper.generate_speech_auto("カスタム単語")

【フォルダ構成】
- {self.base_voice_folder}/     : 音声サンプル保存
- {self.generated_folder}/  : 生成された音声保存

【高品質音声合成のインストール（オプション）】
pip install coqui-tts          # Coqui TTS（高品質）
# eSpeak は公式サイトからダウンロード

====================================="""
        
        return guide

def quick_generate_speech(text, method="auto", output_folder="generated_voices"):
    """
    簡単音声生成関数
    
    Args:
        text (str): 音声化するテキスト
        method (str): 音声合成方法
        output_folder (str): 出力フォルダ
    
    Returns:
        str: 生成された音声ファイルパス
    """
    helper = VoiceSynthesisHelper()
    return helper.generate_speech_auto(text, prefer_method=method)

if __name__ == "__main__":
    print("音声合成ヘルパーのテスト")
    
    helper = VoiceSynthesisHelper()
    
    print("\n" + helper.create_setup_guide())
    
    # テスト音声生成
    test_words = ["こんにちは", "1", "2", "3", "価格", "円"]
    
    print(f"\nテスト音声生成: {test_words}")
    generated = helper.batch_generate_common_words(test_words)
    
    print(f"\n生成結果:")
    for word, file_path in generated.items():
        exists = "✓" if os.path.exists(file_path) else "✗"
        print(f"  {exists} {word} -> {file_path}")