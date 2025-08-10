#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル音声合成テストスクリプト
コマンドラインから簡単に音声合成をテスト
"""

import sys
import os
import argparse
import subprocess
import tempfile
from datetime import datetime

def test_pyttsx3(text, output_file=None):
    """pyttsx3で音声合成テスト"""
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        
        # 日本語音声を探す
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'japanese' in voice.name.lower() or 'japan' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                print(f"日本語音声を設定: {voice.name}")
                break
        
        # 音声設定
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        if output_file:
            # ファイル保存
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            print(f"[pyttsx3] 音声ファイル保存: {output_file}")
        else:
            # 直接再生
            engine.say(text)
            engine.runAndWait()
            print(f"[pyttsx3] 音声再生完了: {text}")
        
        return True
        
    except Exception as e:
        print(f"pyttsx3 エラー: {e}")
        return False

def test_windows_sapi(text, output_file=None):
    """Windows SAPI で音声合成テスト"""
    try:
        import win32com.client
        
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        
        # 日本語音声を探す
        voices = sapi.GetVoices()
        for i in range(voices.Count):
            voice = voices.Item(i)
            desc = voice.GetDescription()
            print(f"利用可能音声: {desc}")
            if 'japan' in desc.lower():
                sapi.Voice = voice
                print(f"日本語音声を設定: {desc}")
                break
        
        if output_file:
            # ファイル保存
            file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
            file_stream.Open(output_file, 3)  # 3 = write mode
            sapi.AudioOutputStream = file_stream
            
            sapi.Speak(text)
            file_stream.Close()
            print(f"[SAPI] 音声ファイル保存: {output_file}")
        else:
            # 直接再生
            sapi.Speak(text)
            print(f"[SAPI] 音声再生完了: {text}")
        
        return True
        
    except Exception as e:
        print(f"Windows SAPI エラー: {e}")
        return False

def test_espeak(text, output_file=None):
    """eSpeak で音声合成テスト"""
    try:
        if output_file:
            cmd = ["espeak", "-v", "ja", "-s", "150", "-w", output_file, text]
        else:
            cmd = ["espeak", "-v", "ja", "-s", "150", text]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if output_file:
                print(f"[eSpeak] 音声ファイル保存: {output_file}")
            else:
                print(f"[eSpeak] 音声再生完了: {text}")
            return True
        else:
            print(f"eSpeak エラー: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("[eSpeak] eSpeakがインストールされていません")
        print("インストール方法: https://espeak.sourceforge.net/download.html")
        return False
    except Exception as e:
        print(f"eSpeak エラー: {e}")
        return False

def test_coqui_tts(text, output_file=None):
    """Coqui TTS で音声合成テスト"""
    try:
        from TTS.api import TTS
        
        print("[Coqui TTS] モデル読み込み中...")
        tts = TTS(model_name="tts_models/ja/kokoro/tacotron2-DDC")
        
        if output_file:
            tts.tts_to_file(text=text, file_path=output_file)
            print(f"[Coqui TTS] 音声ファイル保存: {output_file}")
        else:
            # 一時ファイルに保存して再生
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tts.tts_to_file(text=text, file_path=tmp.name)
                
                try:
                    import pygame
                    pygame.mixer.init()
                    sound = pygame.mixer.Sound(tmp.name)
                    sound.play()
                    
                    # 再生完了まで待機
                    import time
                    while pygame.mixer.get_busy():
                        time.sleep(0.1)
                    
                    print(f"[Coqui TTS] 音声再生完了: {text}")
                except:
                    print(f"[Coqui TTS] 音声ファイル作成完了: {tmp.name}")
                finally:
                    os.unlink(tmp.name)
        
        return True
        
    except ImportError:
        print("[Coqui TTS] Coqui TTSがインストールされていません")
        print("インストール方法: pip install coqui-tts")
        return False
    except Exception as e:
        print(f"Coqui TTS エラー: {e}")
        return False

def batch_test_engines(text, output_dir=None):
    """すべてのエンジンでテスト"""
    engines = [
        ("pyttsx3", test_pyttsx3),
        ("sapi", test_windows_sapi),
        ("espeak", test_espeak),
        ("coqui", test_coqui_tts)
    ]
    
    results = {}
    
    for engine_name, test_func in engines:
        print(f"\n=== {engine_name} テスト ===")
        
        output_file = None
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%H%M%S")
            output_file = os.path.join(output_dir, f"{engine_name}_{timestamp}_{text[:10]}.wav")
        
        success = test_func(text, output_file)
        results[engine_name] = success
        
        if success:
            print(f"✓ {engine_name} 成功")
        else:
            print(f"✗ {engine_name} 失敗")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="音声合成エンジンテストツール")
    parser.add_argument("text", nargs="?", default="こんにちは、音声合成のテストです", 
                       help="音声化するテキスト")
    parser.add_argument("-e", "--engine", choices=["pyttsx3", "sapi", "espeak", "coqui", "all"], 
                       default="all", help="使用するエンジン")
    parser.add_argument("-o", "--output", help="出力ディレクトリ")
    parser.add_argument("--save", action="store_true", help="音声ファイルを保存")
    
    args = parser.parse_args()
    
    print("=== 音声合成テストツール ===")
    print(f"テキスト: '{args.text}'")
    print(f"エンジン: {args.engine}")
    
    if args.save and not args.output:
        args.output = f"voice_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if args.engine == "all":
        print("\\nすべてのエンジンでテスト中...")
        results = batch_test_engines(args.text, args.output)
        
        print("\\n=== テスト結果 ===")
        for engine, success in results.items():
            status = "✓ 成功" if success else "✗ 失敗"
            print(f"{engine:10} : {status}")
    
    else:
        output_file = None
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            timestamp = datetime.now().strftime("%H%M%S")
            output_file = os.path.join(args.output, f"{args.engine}_{timestamp}_{args.text[:10]}.wav")
        
        if args.engine == "pyttsx3":
            test_pyttsx3(args.text, output_file)
        elif args.engine == "sapi":
            test_windows_sapi(args.text, output_file)
        elif args.engine == "espeak":
            test_espeak(args.text, output_file)
        elif args.engine == "coqui":
            test_coqui_tts(args.text, output_file)

def quick_test():
    """クイックテスト実行"""
    test_words = [
        "こんにちは",
        "数字の1です", 
        "価格は100円です",
        "ありがとうございました"
    ]
    
    print("=== クイック音声合成テスト ===")
    
    for word in test_words:
        print(f"\\n'{word}' をテスト中...")
        
        # pyttsx3で簡単テスト
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(word)
            engine.runAndWait()
            print("✓ 再生完了")
        except Exception as e:
            print(f"✗ エラー: {e}")
        
        import time
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 引数なしの場合はクイックテスト
        quick_test()
    else:
        main()