import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os

def open_voice_settings():
    """音声設定画面を開く"""
    try:
        subprocess.run([sys.executable, "voice_config_gui.py"], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("エラー", "音声設定画面の起動に失敗しました")
    except FileNotFoundError:
        messagebox.showerror("エラー", "voice_config_gui.pyが見つかりません")


def start_camera():
    """カメラモードでOCRを起動"""
    try:
        subprocess.run([sys.executable, "ocr_app.py", "camera"], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("エラー", "カメラの起動に失敗しました")
    except FileNotFoundError:
        messagebox.showerror("エラー", "ocr_app.pyが見つかりません")

def select_image():
    """画像ファイルを選択してOCRを実行"""
    file_path = filedialog.askopenfilename(
        title="OCRする画像を選択",
        filetypes=[
            ("画像ファイル", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("すべてのファイル", "*.*")
        ]
    )
    
    if file_path:
        try:
            result = subprocess.run([sys.executable, "ocr_app.py", file_path], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                # 結果を表示するウィンドウを作成
                show_result(result.stdout)
            else:
                messagebox.showerror("エラー", f"OCR処理に失敗しました:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}")

def show_result(text):
    """OCR結果を表示"""
    result_window = tk.Toplevel(root)
    result_window.title("OCR結果")
    result_window.geometry("650x450")
    
    # テキストエリア
    text_area = tk.Text(result_window, wrap=tk.WORD, font=("MS Gothic", 12))
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_area.insert(tk.END, text)
    
    # ボタンフレーム
    button_frame = tk.Frame(result_window)
    button_frame.pack(pady=5)
    
    def speak_result():
        """OCR結果を音声で読み上げ"""
        try:
            from custom_voice_helper import speak_with_custom_voice
            speak_with_custom_voice(text, fallback=True)
        except Exception as e:
            print(f"音声読み上げエラー: {e}")
            messagebox.showwarning("警告", f"音声読み上げに失敗しました: {e}")
    
    def stop_speech():
        """音声停止"""
        try:
            from custom_voice_helper import CustomVoiceHelper
            from text_to_speech_helper import TextToSpeechHelper
            
            custom_helper = CustomVoiceHelper()
            tts_helper = TextToSpeechHelper()
            
            custom_helper.stop_speaking()
            tts_helper.stop_speaking()
        except Exception as e:
            print(f"音声停止エラー: {e}")
    
    # 音声読み上げボタン
    tk.Button(button_frame, text="音声で読み上げ", command=speak_result, 
             font=("MS Gothic", 10), bg="#FFF2CC").pack(side=tk.LEFT, padx=5)
    
    # 停止ボタン
    tk.Button(button_frame, text="停止", command=stop_speech,
             font=("MS Gothic", 10)).pack(side=tk.LEFT, padx=5)
    
    # 閉じるボタン
    tk.Button(button_frame, text="閉じる", command=result_window.destroy,
             font=("MS Gothic", 10)).pack(side=tk.LEFT, padx=5)

# メインウィンドウ作成
root = tk.Tk()
root.title("OCRアプリ")
root.geometry("300x250")
root.resizable(False, False)

# タイトル
title_label = tk.Label(root, text="OCR文字認識アプリ", font=("MS Gothic", 16, "bold"))
title_label.pack(pady=20)

# ボタン
camera_btn = tk.Button(root, text="カメラで文字認識", command=start_camera, 
                      width=20, height=2, font=("MS Gothic", 12))
camera_btn.pack(pady=5)

image_btn = tk.Button(root, text="画像ファイルから認識", command=select_image,
                     width=20, height=2, font=("MS Gothic", 12))
image_btn.pack(pady=5)

# 音声設定ボタンを追加
voice_btn = tk.Button(root, text="音声設定", command=open_voice_settings,
                     width=20, height=2, font=("MS Gothic", 12), bg="#E8F4FD")
voice_btn.pack(pady=5)

# 作業ディレクトリをスクリプトのディレクトリに変更
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

root.mainloop()