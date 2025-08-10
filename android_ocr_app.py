#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android対応OCRアプリ - Kivy版
元のTkinterアプリをKivyに移植してAndroid対応
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.camera import Camera
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.logger import Logger

import os
import sys
from datetime import datetime
import threading

# Android権限チェック
try:
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from jnius import autoclass
    ANDROID = True
    Logger.info('OCR: Android環境を検出')
except ImportError:
    ANDROID = False
    Logger.info('OCR: デスクトップ環境で動作')

# OCR関連のインポート
try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    Logger.warning('OCR: OpenCV/PILが利用できません')

# 音声合成関連
try:
    if ANDROID:
        # Android用音声合成 (TTS)
        from jnius import autoclass
        AndroidTTS = autoclass('android.speech.tts.TextToSpeech')
        Locale = autoclass('java.util.Locale')
        TTS_AVAILABLE = True
    else:
        # Windows用音声合成
        import pyttsx3
        TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    Logger.warning('OCR: 音声合成が利用できません')

class MainScreen(Screen):
    """メイン画面"""
    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.name = 'main'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # タイトル
        title = Label(
            text='OCR文字認識アプリ',
            font_size='24sp',
            size_hint=(1, 0.2),
            color=(0, 0, 0.8, 1)
        )
        layout.add_widget(title)
        
        # カメラボタン
        camera_btn = Button(
            text='カメラで文字認識',
            size_hint=(1, 0.2),
            font_size='18sp'
        )
        camera_btn.bind(on_press=self.open_camera)
        layout.add_widget(camera_btn)
        
        # ファイル選択ボタン
        file_btn = Button(
            text='画像ファイルから認識',
            size_hint=(1, 0.2),
            font_size='18sp'
        )
        file_btn.bind(on_press=self.open_file_chooser)
        layout.add_widget(file_btn)
        
        # 音声設定ボタン
        voice_btn = Button(
            text='音声設定',
            size_hint=(1, 0.15),
            font_size='16sp',
            background_color=(0.9, 0.95, 1, 1)
        )
        voice_btn.bind(on_press=self.open_voice_settings)
        layout.add_widget(voice_btn)
        
        # 情報ラベル
        info_text = "Android版OCR文字認識アプリ\\n"
        if ANDROID:
            info_text += "✓ Android環境で動作中"
        else:
            info_text += "✓ デスクトップ環境で動作中"
            
        info_label = Label(
            text=info_text,
            size_hint=(1, 0.15),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(info_label)
        
        self.add_widget(layout)
        
        # Android権限要求
        if ANDROID:
            self.request_android_permissions()
    
    def request_android_permissions(self):
        """Android権限を要求"""
        try:
            permissions = [
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.RECORD_AUDIO
            ]
            request_permissions(permissions)
            Logger.info('OCR: Android権限を要求しました')
        except Exception as e:
            Logger.error(f'OCR: 権限要求エラー: {e}')
    
    def open_camera(self, instance):
        """カメラ画面を開く"""
        self.manager.current = 'camera'
    
    def open_file_chooser(self, instance):
        """ファイル選択画面を開く"""
        self.manager.current = 'filechooser'
    
    def open_voice_settings(self, instance):
        """音声設定画面を開く"""
        self.manager.current = 'voice_settings'

class CameraScreen(Screen):
    """カメラ画面"""
    
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.name = 'camera'
        
        layout = BoxLayout(orientation='vertical')
        
        # カメラウィジェット
        if CV2_AVAILABLE:
            self.camera = Camera(
                resolution=(640, 480),
                play=True
            )
            layout.add_widget(self.camera)
        else:
            # カメラが利用できない場合
            no_camera_label = Label(
                text='カメラが利用できません\\nCV2ライブラリをインストールしてください',
                font_size='16sp'
            )
            layout.add_widget(no_camera_label)
        
        # ボタンレイアウト
        button_layout = BoxLayout(size_hint=(1, 0.2), spacing=10, padding=10)
        
        # 撮影ボタン
        capture_btn = Button(
            text='撮影・OCR実行',
            font_size='16sp'
        )
        capture_btn.bind(on_press=self.capture_and_ocr)
        button_layout.add_widget(capture_btn)
        
        # 戻るボタン
        back_btn = Button(
            text='戻る',
            font_size='16sp'
        )
        back_btn.bind(on_press=self.go_back)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def capture_and_ocr(self, instance):
        """撮影してOCR実行"""
        if not hasattr(self, 'camera'):
            self.show_popup('エラー', 'カメラが利用できません')
            return
        
        try:
            # カメラから画像をキャプチャ
            self.camera.export_to_png("temp_capture.png")
            
            # OCR実行
            Clock.schedule_once(lambda dt: self.process_captured_image(), 1)
            
        except Exception as e:
            self.show_popup('エラー', f'撮影エラー: {str(e)}')
    
    def process_captured_image(self):
        """キャプチャした画像を処理"""
        try:
            if CV2_AVAILABLE:
                result_text = self.perform_ocr("temp_capture.png")
                self.show_ocr_result(result_text)
            else:
                self.show_popup('エラー', 'OCR機能が利用できません')
        except Exception as e:
            self.show_popup('エラー', f'OCR処理エラー: {str(e)}')
    
    def perform_ocr(self, image_path):
        """OCR処理を実行"""
        try:
            if ANDROID:
                # Android用OCR (Google ML Kit使用)
                return self.android_ocr(image_path)
            else:
                # デスクトップ用OCR (Tesseract使用)
                return self.desktop_ocr(image_path)
        except Exception as e:
            Logger.error(f'OCR: OCR処理エラー: {e}')
            return f"OCR処理中にエラーが発生しました: {str(e)}"
    
    def android_ocr(self, image_path):
        """Android用OCR (Google ML Kit)"""
        try:
            # Google ML Kitを使用したOCR実装
            # 注: 実際の実装にはGoogle ML Kit for Androidが必要
            Logger.info('OCR: Android OCR実行中...')
            
            # 簡易実装（実際にはML Kitを使用）
            return "Android OCR機能（ML Kit）は実装中です。\\n現在はサンプルテキストを表示しています。"
            
        except Exception as e:
            Logger.error(f'OCR: Android OCR エラー: {e}')
            return f"Android OCR エラー: {str(e)}"
    
    def desktop_ocr(self, image_path):
        """デスクトップ用OCR (Tesseract)"""
        try:
            # 元のOCRロジックを使用
            img = cv2.imread(image_path)
            if img is None:
                return "画像の読み込みに失敗しました"
            
            # グレースケール変換
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 二値化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Tesseract OCR (利用可能な場合)
            try:
                import pytesseract
                text = pytesseract.image_to_string(binary, lang='jpn')
                return text if text.strip() else "文字が検出されませんでした"
            except ImportError:
                return "Tesseract OCRが利用できません。\\npytesseractをインストールしてください。"
                
        except Exception as e:
            Logger.error(f'OCR: デスクトップOCR エラー: {e}')
            return f"デスクトップOCR エラー: {str(e)}"
    
    def show_ocr_result(self, text):
        """OCR結果を表示"""
        result_screen = self.manager.get_screen('result')
        result_screen.set_result(text)
        self.manager.current = 'result'
    
    def show_popup(self, title, message):
        """ポップアップを表示"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label = Label(text=message, font_size='14sp')
        content.add_widget(label)
        
        close_btn = Button(text='閉じる', size_hint=(1, 0.3), font_size='14sp')
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        """メイン画面に戻る"""
        self.manager.current = 'main'

class FileChooserScreen(Screen):
    """ファイル選択画面"""
    
    def __init__(self, **kwargs):
        super(FileChooserScreen, self).__init__(**kwargs)
        self.name = 'filechooser'
        
        layout = BoxLayout(orientation='vertical')
        
        # ファイル選択
        self.filechooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.bmp'],
            size_hint=(1, 0.8)
        )
        layout.add_widget(self.filechooser)
        
        # ボタンレイアウト
        button_layout = BoxLayout(size_hint=(1, 0.2), spacing=10, padding=10)
        
        # 選択ボタン
        select_btn = Button(text='選択してOCR実行', font_size='16sp')
        select_btn.bind(on_press=self.select_and_ocr)
        button_layout.add_widget(select_btn)
        
        # 戻るボタン
        back_btn = Button(text='戻る', font_size='16sp')
        back_btn.bind(on_press=self.go_back)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def select_and_ocr(self, instance):
        """選択したファイルでOCR実行"""
        if self.filechooser.selection:
            file_path = self.filechooser.selection[0]
            
            # OCR実行
            camera_screen = self.manager.get_screen('camera')
            result_text = camera_screen.perform_ocr(file_path)
            camera_screen.show_ocr_result(result_text)
        else:
            self.show_popup('エラー', 'ファイルを選択してください')
    
    def show_popup(self, title, message):
        """ポップアップを表示"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label = Label(text=message, font_size='14sp')
        content.add_widget(label)
        
        close_btn = Button(text='閉じる', size_hint=(1, 0.3), font_size='14sp')
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        """メイン画面に戻る"""
        self.manager.current = 'main'

class ResultScreen(Screen):
    """結果表示画面"""
    
    def __init__(self, **kwargs):
        super(ResultScreen, self).__init__(**kwargs)
        self.name = 'result'
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # タイトル
        title = Label(
            text='OCR結果',
            font_size='20sp',
            size_hint=(1, 0.1),
            color=(0, 0, 0.8, 1)
        )
        layout.add_widget(title)
        
        # 結果表示エリア
        scroll = ScrollView(size_hint=(1, 0.7))
        self.result_label = Label(
            text='',
            font_size='14sp',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        scroll.add_widget(self.result_label)
        layout.add_widget(scroll)
        
        # ボタンレイアウト
        button_layout = BoxLayout(size_hint=(1, 0.2), spacing=10, padding=10)
        
        # 音声読み上げボタン
        if TTS_AVAILABLE:
            speak_btn = Button(
                text='音声で読み上げ',
                font_size='14sp',
                background_color=(1, 1, 0.8, 1)
            )
            speak_btn.bind(on_press=self.speak_result)
            button_layout.add_widget(speak_btn)
        
        # 戻るボタン
        back_btn = Button(text='戻る', font_size='14sp')
        back_btn.bind(on_press=self.go_back)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
        
        # 音声合成初期化
        if TTS_AVAILABLE and ANDROID:
            self.init_android_tts()
    
    def init_android_tts(self):
        """Android TTS初期化"""
        try:
            # Android TTS初期化 (実際の実装時に使用)
            Logger.info('OCR: Android TTS初期化中...')
            # self.tts = AndroidTTS(mActivity, None)
            # self.tts.setLanguage(Locale.JAPANESE)
        except Exception as e:
            Logger.error(f'OCR: Android TTS初期化エラー: {e}')
    
    def set_result(self, text):
        """結果テキストを設定"""
        self.result_text = text
        self.result_label.text = text
        self.result_label.text_size = (400, None)  # 適切な幅を設定
    
    def speak_result(self, instance):
        """結果を音声で読み上げ"""
        if not hasattr(self, 'result_text') or not self.result_text:
            return
        
        try:
            if ANDROID:
                self.android_speak(self.result_text)
            else:
                self.desktop_speak(self.result_text)
        except Exception as e:
            Logger.error(f'OCR: 音声読み上げエラー: {e}')
    
    def android_speak(self, text):
        """Android TTS で読み上げ"""
        try:
            # Android TTS実装 (実際の実装時に使用)
            Logger.info(f'OCR: Android TTS読み上げ: {text[:30]}...')
            # self.tts.speak(text, AndroidTTS.QUEUE_FLUSH, None, "OCR_SPEECH")
        except Exception as e:
            Logger.error(f'OCR: Android TTS エラー: {e}')
    
    def desktop_speak(self, text):
        """デスクトップ TTS で読み上げ"""
        try:
            def speak_worker():
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            
            thread = threading.Thread(target=speak_worker)
            thread.daemon = True
            thread.start()
            Logger.info(f'OCR: デスクトップTTS読み上げ: {text[:30]}...')
            
        except Exception as e:
            Logger.error(f'OCR: デスクトップTTS エラー: {e}')
    
    def go_back(self, instance):
        """メイン画面に戻る"""
        self.manager.current = 'main'

class VoiceSettingsScreen(Screen):
    """音声設定画面"""
    
    def __init__(self, **kwargs):
        super(VoiceSettingsScreen, self).__init__(**kwargs)
        self.name = 'voice_settings'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # タイトル
        title = Label(
            text='音声設定',
            font_size='20sp',
            size_hint=(1, 0.15),
            color=(0, 0, 0.8, 1)
        )
        layout.add_widget(title)
        
        # 設定項目
        settings_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.7))
        
        # 音声エンジン情報
        engine_info = "音声エンジン: "
        if ANDROID:
            engine_info += "Android TTS"
        else:
            engine_info += "pyttsx3 (Windows)"
            
        engine_label = Label(
            text=engine_info,
            font_size='14sp',
            size_hint=(1, 0.2)
        )
        settings_layout.add_widget(engine_label)
        
        # テスト用テキスト入力
        test_label = Label(
            text='テスト読み上げテキスト:',
            font_size='14sp',
            size_hint=(1, 0.2)
        )
        settings_layout.add_widget(test_label)
        
        self.test_input = TextInput(
            text='こんにちは。音声テストです。',
            multiline=False,
            size_hint=(1, 0.2),
            font_size='14sp'
        )
        settings_layout.add_widget(self.test_input)
        
        # テストボタン
        test_btn = Button(
            text='音声テスト',
            size_hint=(1, 0.2),
            font_size='16sp',
            background_color=(0.8, 1, 0.8, 1)
        )
        test_btn.bind(on_press=self.test_speech)
        settings_layout.add_widget(test_btn)
        
        layout.add_widget(settings_layout)
        
        # 戻るボタン
        back_btn = Button(
            text='戻る',
            size_hint=(1, 0.15),
            font_size='16sp'
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def test_speech(self, instance):
        """音声テスト"""
        test_text = self.test_input.text
        if not test_text:
            return
        
        result_screen = self.manager.get_screen('result')
        if ANDROID:
            result_screen.android_speak(test_text)
        else:
            result_screen.desktop_speak(test_text)
    
    def go_back(self, instance):
        """メイン画面に戻る"""
        self.manager.current = 'main'

class OCRApp(App):
    """メインアプリケーション"""
    
    def build(self):
        """アプリをビルド"""
        Logger.info('OCR: Android OCRアプリを起動中...')
        
        # 画面マネージャー
        sm = ScreenManager()
        
        # 各画面を追加
        sm.add_widget(MainScreen())
        sm.add_widget(CameraScreen())
        sm.add_widget(FileChooserScreen())
        sm.add_widget(ResultScreen())
        sm.add_widget(VoiceSettingsScreen())
        
        return sm

if __name__ == '__main__':
    OCRApp().run()