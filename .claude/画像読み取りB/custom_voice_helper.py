import pygame
import os
import tempfile
import hashlib
from pathlib import Path
import json
import time
import threading

class CustomVoiceHelper:
    """
    カスタム音声再生ヘルパークラス
    事前録音した音声ファイルを使用してOCR結果を読み上げ
    """
    
    def __init__(self, voice_folder="custom_voices"):
        """
        Args:
            voice_folder (str): カスタム音声ファイルを保存するフォルダ
        """
        self.voice_folder = voice_folder
        self.voice_mapping = {}
        self.pygame_mixer = None
        self.current_thread = None
        self.is_playing = False
        
        self._initialize_pygame()
        self._load_voice_mapping()
    
    def _initialize_pygame(self):
        """pygame音声システムを初期化"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_mixer = pygame.mixer
            print("[OK] pygame音声システムを初期化しました")
        except Exception as e:
            print(f"pygame初期化エラー: {e}")
            self.pygame_mixer = None
    
    def _load_voice_mapping(self):
        """音声マッピングファイルを読み込み"""
        mapping_file = os.path.join(self.voice_folder, "voice_mapping.json")
        
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.voice_mapping = json.load(f)
                print(f"[OK] 音声マッピングを読み込み: {len(self.voice_mapping)}件")
            except Exception as e:
                print(f"音声マッピング読み込みエラー: {e}")
                self.voice_mapping = {}
        else:
            print(f"[INFO] 音声マッピングファイルが見つかりません: {mapping_file}")
            self._create_default_mapping()
    
    def _create_default_mapping(self):
        """デフォルト音声マッピングを作成"""
        os.makedirs(self.voice_folder, exist_ok=True)
        
        # デフォルトマッピング例
        default_mapping = {
            # よく使われるフレーズの音声ファイルマッピング
            "こんにちは": "hello.wav",
            "ありがとうございます": "thank_you.wav", 
            "すみません": "excuse_me.wav",
            "こんばんは": "good_evening.wav",
            "おはようございます": "good_morning.wav",
            # 数字
            "0": "num_0.wav", "1": "num_1.wav", "2": "num_2.wav",
            "3": "num_3.wav", "4": "num_4.wav", "5": "num_5.wav",
            "6": "num_6.wav", "7": "num_7.wav", "8": "num_8.wav",
            "9": "num_9.wav", "10": "num_10.wav",
            # よく読み取られる文字
            "円": "yen.wav",
            "価格": "price.wav",
            "商品名": "product_name.wav"
        }
        
        self.voice_mapping = default_mapping
        self._save_voice_mapping()
    
    def _save_voice_mapping(self):
        """音声マッピングを保存"""
        mapping_file = os.path.join(self.voice_folder, "voice_mapping.json")
        os.makedirs(self.voice_folder, exist_ok=True)
        
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_mapping, f, ensure_ascii=False, indent=2)
            print(f"[OK] 音声マッピングを保存: {mapping_file}")
        except Exception as e:
            print(f"音声マッピング保存エラー: {e}")
    
    def add_voice_file(self, text, audio_file_path):
        """
        テキストと音声ファイルの対応を追加
        
        Args:
            text (str): テキスト
            audio_file_path (str): 音声ファイルのパス
        """
        if not os.path.exists(audio_file_path):
            print(f"[ERROR] 音声ファイルが見つかりません: {audio_file_path}")
            return False
        
        # 音声ファイルをカスタムボイスフォルダにコピー
        filename = f"{hashlib.md5(text.encode()).hexdigest()}.wav"
        dest_path = os.path.join(self.voice_folder, filename)
        
        try:
            import shutil
            shutil.copy2(audio_file_path, dest_path)
            
            # マッピングに追加
            self.voice_mapping[text] = filename
            self._save_voice_mapping()
            
            print(f"[OK] 音声ファイルを追加: '{text}' -> {filename}")
            return True
            
        except Exception as e:
            print(f"音声ファイル追加エラー: {e}")
            return False
    
    def speak_text(self, text, fallback_engine=None):
        """
        カスタム音声でテキストを読み上げ
        
        Args:
            text (str): 読み上げるテキスト
            fallback_engine: カスタム音声がない場合のフォールバック
        """
        if not self.pygame_mixer:
            print("[ERROR] pygame音声システムが利用できません")
            return False
        
        # 現在の再生を停止
        self.stop_speaking()
        
        # 非同期で再生開始
        self.current_thread = threading.Thread(
            target=self._play_custom_voice,
            args=(text, fallback_engine)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
        
        return True
    
    def _play_custom_voice(self, text, fallback_engine):
        """カスタム音声再生のワーカー"""
        try:
            self.is_playing = True
            
            # 完全一致の音声ファイルを探す
            audio_file = self._find_audio_file(text)
            
            if audio_file:
                print(f"[CUSTOM] カスタム音声で再生: {text[:30]}...")
                self._play_audio_file(audio_file)
            else:
                # 部分一致や単語分割を試す
                played = self._play_partial_match(text)
                
                if not played and fallback_engine:
                    print(f"[FALLBACK] 標準音声で再生: {text[:30]}...")
                    fallback_engine.speak_text(text, async_mode=False)
                elif not played:
                    print(f"[WARNING] 音声ファイルが見つかりません: {text}")
            
        except Exception as e:
            print(f"カスタム音声再生エラー: {e}")
        finally:
            self.is_playing = False
    
    def _find_audio_file(self, text):
        """テキストに対応する音声ファイルを探す"""
        # 完全一致
        if text in self.voice_mapping:
            filename = self.voice_mapping[text]
            file_path = os.path.join(self.voice_folder, filename)
            if os.path.exists(file_path):
                return file_path
        
        # 大文字小文字を無視して検索
        text_lower = text.lower()
        for key, filename in self.voice_mapping.items():
            if key.lower() == text_lower:
                file_path = os.path.join(self.voice_folder, filename)
                if os.path.exists(file_path):
                    return file_path
        
        return None
    
    def _play_partial_match(self, text):
        """部分一致や単語分割で音声を再生"""
        words_played = False
        
        # 単語ごとに分割して再生を試す
        words = text.split()
        for word in words:
            word = word.strip('.,!?。、！？')
            audio_file = self._find_audio_file(word)
            if audio_file:
                self._play_audio_file(audio_file)
                words_played = True
                time.sleep(0.5)  # 単語間の間隔
        
        return words_played
    
    def _play_audio_file(self, audio_file_path):
        """音声ファイルを再生"""
        try:
            sound = pygame.mixer.Sound(audio_file_path)
            sound.play()
            
            # 再生完了まで待機
            while pygame.mixer.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"音声ファイル再生エラー: {e}")
    
    def stop_speaking(self):
        """音声再生を停止"""
        try:
            if self.pygame_mixer:
                pygame.mixer.stop()
            
            if self.current_thread and self.current_thread.is_alive():
                time.sleep(0.2)
            
            self.is_playing = False
            print("[STOP] カスタム音声を停止")
            
        except Exception as e:
            print(f"カスタム音声停止エラー: {e}")
    
    def get_voice_list(self):
        """登録されている音声の一覧を取得"""
        voice_list = []
        for text, filename in self.voice_mapping.items():
            file_path = os.path.join(self.voice_folder, filename)
            exists = os.path.exists(file_path)
            voice_list.append({
                'text': text,
                'filename': filename,
                'exists': exists,
                'path': file_path
            })
        
        return voice_list
    
    def create_voice_setup_guide(self):
        """音声ファイル準備ガイドを表示"""
        guide = """
=== カスタム音声セットアップガイド ===

1. 音声ファイルの準備:
   - WAV形式のファイルを用意
   - サンプルレート: 22050Hz推奨
   - ビット深度: 16bit推奨
   - 1-5秒程度の短い音声が最適

2. 音声フォルダ:
   {voice_folder}

3. 音声ファイル追加方法:
   helper.add_voice_file("こんにちは", "hello.wav")

4. 現在の音声マッピング:
""".format(voice_folder=os.path.abspath(self.voice_folder))
        
        for text, filename in self.voice_mapping.items():
            file_path = os.path.join(self.voice_folder, filename)
            status = "✓" if os.path.exists(file_path) else "✗"
            guide += f"   {status} '{text}' -> {filename}\n"
        
        guide += """
5. 使用例:
   from custom_voice_helper import CustomVoiceHelper
   helper = CustomVoiceHelper()
   helper.speak_text("こんにちは")

====================================="""
        
        return guide

# 簡単使用用の関数
def speak_with_custom_voice(text, voice_folder="custom_voices", fallback=True):
    """
    カスタム音声で簡単に読み上げ
    
    Args:
        text (str): 読み上げるテキスト
        voice_folder (str): カスタム音声フォルダ
        fallback (bool): フォールバックを使用するか
    """
    helper = CustomVoiceHelper(voice_folder)
    
    if fallback:
        # フォールバック用の標準音声エンジンを準備
        try:
            from text_to_speech_helper import TextToSpeechHelper
            fallback_engine = TextToSpeechHelper()
        except:
            fallback_engine = None
    else:
        fallback_engine = None
    
    return helper.speak_text(text, fallback_engine)

if __name__ == "__main__":
    # テスト実行
    print("カスタム音声ヘルパーのテスト")
    
    helper = CustomVoiceHelper()
    
    print("\n" + helper.create_voice_setup_guide())
    
    # テスト音声の追加（実際の音声ファイルがある場合）
    test_texts = ["こんにちは", "ありがとうございます", "1", "2", "3"]
    
    print(f"\nテスト音声を再生中...")
    for text in test_texts:
        print(f"再生: '{text}'")
        helper.speak_text(text)
        time.sleep(2)