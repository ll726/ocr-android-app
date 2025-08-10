import pyttsx3
import win32com.client
import threading
import time
from datetime import datetime
import os

class TextToSpeechHelper:
    """
    テキスト読み上げヘルパークラス
    OCR結果を音声で読み上げる機能を提供
    """
    
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.current_thread = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """音声合成エンジンを初期化"""
        try:
            # pyttsx3エンジンを初期化
            self.engine = pyttsx3.init()
            
            # 日本語音声の設定を試行
            voices = self.engine.getProperty('voices')
            japanese_voice = None
            
            for voice in voices:
                if 'japanese' in voice.name.lower() or 'japan' in voice.name.lower():
                    japanese_voice = voice
                    break
            
            if japanese_voice:
                self.engine.setProperty('voice', japanese_voice.id)
                print(f"[OK] 日本語音声を設定: {japanese_voice.name}")
            else:
                print("[INFO] 日本語音声が見つかりません。デフォルト音声を使用")
            
            # 音声設定
            self.engine.setProperty('rate', 150)    # 読み上げ速度
            self.engine.setProperty('volume', 0.9)  # 音量
            
            print("[OK] 音声合成エンジンを初期化しました")
            
        except Exception as e:
            print(f"音声合成エンジン初期化エラー: {e}")
            self.engine = None
    
    def speak_text(self, text, async_mode=True):
        """
        テキストを音声で読み上げ
        
        Args:
            text (str): 読み上げるテキスト
            async_mode (bool): 非同期実行するか
        """
        if not self.engine:
            print("[ERROR] 音声合成エンジンが利用できません")
            return False
        
        if not text or text.strip() == "":
            print("[WARNING] 読み上げるテキストが空です")
            return False
        
        try:
            # 現在の読み上げを停止
            self.stop_speaking()
            
            if async_mode:
                # 非同期で読み上げ
                self.current_thread = threading.Thread(
                    target=self._speak_worker, 
                    args=(text,)
                )
                self.current_thread.daemon = True
                self.current_thread.start()
            else:
                # 同期で読み上げ
                self._speak_worker(text)
            
            return True
            
        except Exception as e:
            print(f"読み上げエラー: {e}")
            return False
    
    def _speak_worker(self, text):
        """読み上げ処理のワーカー関数"""
        try:
            self.is_speaking = True
            print(f"[SPEAKING] 読み上げ開始: {text[:30]}...")
            
            # テキストを読み上げ
            self.engine.say(text)
            self.engine.runAndWait()
            
            print("[SPEAKING] 読み上げ完了")
            
        except Exception as e:
            print(f"読み上げワーカーエラー: {e}")
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        """読み上げを停止"""
        try:
            if self.is_speaking and self.engine:
                self.engine.stop()
                print("[STOP] 読み上げを停止しました")
            
            # スレッドが実行中なら少し待つ
            if self.current_thread and self.current_thread.is_alive():
                time.sleep(0.5)
            
            self.is_speaking = False
            
        except Exception as e:
            print(f"読み上げ停止エラー: {e}")
    
    def set_voice_properties(self, rate=None, volume=None):
        """
        音声プロパティを設定
        
        Args:
            rate (int): 読み上げ速度 (50-300)
            volume (float): 音量 (0.0-1.0)
        """
        if not self.engine:
            return False
        
        try:
            if rate is not None:
                self.engine.setProperty('rate', max(50, min(300, rate)))
                print(f"[OK] 読み上げ速度を設定: {rate}")
            
            if volume is not None:
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
                print(f"[OK] 音量を設定: {volume}")
            
            return True
            
        except Exception as e:
            print(f"音声プロパティ設定エラー: {e}")
            return False
    
    def get_available_voices(self):
        """利用可能な音声の一覧を取得"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'language': getattr(voice, 'languages', ['Unknown']),
                    'index': i
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            print(f"音声一覧取得エラー: {e}")
            return []
    
    def set_voice_by_index(self, voice_index):
        """インデックスで音声を設定"""
        if not self.engine:
            return False
        
        try:
            voices = self.engine.getProperty('voices')
            if 0 <= voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                print(f"[OK] 音声を変更: {voices[voice_index].name}")
                return True
            else:
                print(f"[ERROR] 無効な音声インデックス: {voice_index}")
                return False
                
        except Exception as e:
            print(f"音声設定エラー: {e}")
            return False
    
    def save_audio_file(self, text, filename=None):
        """
        テキストを音声ファイルに保存
        
        Args:
            text (str): 音声化するテキスト
            filename (str): 保存ファイル名（Noneなら自動生成）
        """
        if not self.engine:
            return None
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ocr_speech_{timestamp}.wav"
            
            # 音声ファイルに保存
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            
            if os.path.exists(filename):
                print(f"[OK] 音声ファイルを保存: {filename}")
                return filename
            else:
                print("[ERROR] 音声ファイルの保存に失敗")
                return None
                
        except Exception as e:
            print(f"音声ファイル保存エラー: {e}")
            return None

class WindowsSAPIHelper:
    """
    Windows SAPI (Speech API) を使用した読み上げヘルパー
    より自然な日本語読み上げが可能
    """
    
    def __init__(self):
        self.sapi = None
        self.is_speaking = False
        self._initialize_sapi()
    
    def _initialize_sapi(self):
        """Windows SAPI を初期化"""
        try:
            self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
            
            # 利用可能な音声を確認
            voices = self.sapi.GetVoices()
            print(f"[OK] Windows SAPI初期化完了 ({voices.Count}個の音声)")
            
            # 日本語音声を探す
            for i in range(voices.Count):
                voice = voices.Item(i)
                if 'japan' in voice.GetDescription().lower():
                    self.sapi.Voice = voice
                    print(f"[OK] 日本語音声を設定: {voice.GetDescription()}")
                    break
            
        except Exception as e:
            print(f"Windows SAPI初期化エラー: {e}")
            self.sapi = None
    
    def speak_text(self, text, async_mode=True):
        """Windows SAPI でテキストを読み上げ"""
        if not self.sapi:
            return False
        
        try:
            flags = 1 if async_mode else 0  # 1=非同期, 0=同期
            self.sapi.Speak(text, flags)
            print(f"[SAPI] 読み上げ: {text[:30]}...")
            return True
            
        except Exception as e:
            print(f"SAPI読み上げエラー: {e}")
            return False
    
    def stop_speaking(self):
        """読み上げ停止"""
        try:
            if self.sapi:
                self.sapi.Speak("", 2)  # 2=停止フラグ
                print("[SAPI] 読み上げを停止")
        except Exception as e:
            print(f"SAPI停止エラー: {e}")

def quick_speak(text, engine="pyttsx3", async_mode=True):
    """
    テキストを素早く読み上げ
    
    Args:
        text (str): 読み上げるテキスト
        engine (str): エンジン種別 ("pyttsx3" or "sapi")
        async_mode (bool): 非同期実行
    """
    try:
        if engine.lower() == "sapi":
            helper = WindowsSAPIHelper()
        else:
            helper = TextToSpeechHelper()
        
        return helper.speak_text(text, async_mode)
        
    except Exception as e:
        print(f"読み上げエラー: {e}")
        return False

def show_voice_settings_menu():
    """音声設定メニューを表示"""
    helper = TextToSpeechHelper()
    voices = helper.get_available_voices()
    
    print("\n=== 利用可能な音声 ===")
    for voice in voices:
        print(f"{voice['index']}: {voice['name']}")
    print("=====================")
    
    return voices

if __name__ == "__main__":
    # テスト実行
    print("音声読み上げ機能のテスト")
    
    test_text = "こんにちは。これはOCRで読み取った文字の読み上げテストです。日本語の音声合成が正常に動作しているかを確認します。"
    
    print("\n1. pyttsx3 エンジンでテスト")
    helper1 = TextToSpeechHelper()
    helper1.speak_text(test_text, async_mode=False)
    
    print("\n2. Windows SAPI でテスト")
    helper2 = WindowsSAPIHelper()
    helper2.speak_text(test_text, async_mode=False)
    
    print("\n3. 利用可能な音声一覧")
    show_voice_settings_menu()