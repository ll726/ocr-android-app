import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from custom_voice_helper import CustomVoiceHelper
from text_to_speech_helper import TextToSpeechHelper
import pygame
import threading

class VoiceConfigGUI:
    """
    音声設定用GUIクラス
    カスタム音声の追加・管理・テストを行う
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("音声設定")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 音声ヘルパー初期化
        self.custom_helper = CustomVoiceHelper()
        self.tts_helper = TextToSpeechHelper()
        
        self.setup_ui()
        self.refresh_voice_list()
    
    def setup_ui(self):
        """UIセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="音声設定", font=("MS Gothic", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 音声エンジン選択フレーム
        engine_frame = ttk.LabelFrame(main_frame, text="音声エンジン選択", padding="10")
        engine_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.engine_var = tk.StringVar(value="custom")
        ttk.Radiobutton(engine_frame, text="カスタム音声 (推奨)", variable=self.engine_var, value="custom").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(engine_frame, text="標準音声エンジン", variable=self.engine_var, value="tts").grid(row=0, column=1, sticky=tk.W)
        
        # テスト再生フレーム
        test_frame = ttk.Frame(main_frame)
        test_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(test_frame, text="テスト文字列:").grid(row=0, column=0, sticky=tk.W)
        self.test_text = tk.StringVar(value="こんにちは")\n        test_entry = ttk.Entry(test_frame, textvariable=self.test_text, width=30)
        test_entry.grid(row=0, column=1, padx=(5, 5), sticky=(tk.W, tk.E))
        
        ttk.Button(test_frame, text="音声テスト", command=self.test_voice).grid(row=0, column=2)
        ttk.Button(test_frame, text="停止", command=self.stop_voice).grid(row=0, column=3, padx=(5, 0))
        
        test_frame.columnconfigure(1, weight=1)
        
        # カスタム音声管理フレーム
        custom_frame = ttk.LabelFrame(main_frame, text="カスタム音声管理", padding="10")
        custom_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 音声リスト
        list_frame = ttk.Frame(custom_frame)
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview for voice list
        columns = ("text", "filename", "status")
        self.voice_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        self.voice_tree.heading("text", text="テキスト")
        self.voice_tree.heading("filename", text="ファイル名")
        self.voice_tree.heading("status", text="状態")
        
        self.voice_tree.column("text", width=200)
        self.voice_tree.column("filename", width=150)
        self.voice_tree.column("status", width=80)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.voice_tree.yview)
        self.voice_tree.configure(yscrollcommand=scrollbar.set)
        
        self.voice_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 音声追加フレーム
        add_frame = ttk.Frame(custom_frame)
        add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(add_frame, text="テキスト:").grid(row=0, column=0, sticky=tk.W)
        self.add_text = tk.StringVar()
        add_text_entry = ttk.Entry(add_frame, textvariable=self.add_text, width=20)
        add_text_entry.grid(row=0, column=1, padx=(5, 5), sticky=(tk.W, tk.E))
        
        ttk.Button(add_frame, text="音声ファイル選択", command=self.select_audio_file).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(add_frame, text="追加", command=self.add_voice_mapping).grid(row=0, column=3)
        
        self.selected_audio_file = tk.StringVar()\n        audio_file_label = ttk.Label(add_frame, textvariable=self.selected_audio_file, foreground="blue")
        audio_file_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        add_frame.columnconfigure(1, weight=1)
        
        # ボタンフレーム
        button_frame = ttk.Frame(custom_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="更新", command=self.refresh_voice_list).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="選択項目削除", command=self.delete_selected_voice).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="フォルダを開く", command=self.open_voice_folder).grid(row=0, column=2, padx=(0, 5))
        
        # 設定の適用・保存フレーム
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(action_frame, text="設定を保存", command=self.save_settings).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(action_frame, text="OCRアプリに戻る", command=self.close_window).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(action_frame, text="ヘルプ", command=self.show_help).grid(row=0, column=2)
        
        # グリッド設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        custom_frame.columnconfigure(0, weight=1)
        custom_frame.rowconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def refresh_voice_list(self):
        """音声リストを更新"""
        # 既存のアイテムをクリア
        for item in self.voice_tree.get_children():
            self.voice_tree.delete(item)
        
        # 音声リストを取得して表示
        voice_list = self.custom_helper.get_voice_list()
        for voice in voice_list:
            status = "✓ 有効" if voice['exists'] else "✗ 無効"
            self.voice_tree.insert("", tk.END, values=(
                voice['text'],
                voice['filename'],
                status
            ))
    
    def test_voice(self):
        """音声テスト"""
        text = self.test_text.get().strip()
        if not text:
            messagebox.showwarning("警告", "テスト文字列を入力してください")
            return
        
        engine = self.engine_var.get()
        
        try:
            if engine == "custom":
                self.custom_helper.speak_text(text, fallback_engine=self.tts_helper)
                print(f"[TEST] カスタム音声でテスト: {text}")
            else:
                self.tts_helper.speak_text(text)
                print(f"[TEST] 標準音声でテスト: {text}")
                
        except Exception as e:
            messagebox.showerror("エラー", f"音声テストに失敗しました: {e}")
    
    def stop_voice(self):
        """音声停止"""
        try:
            self.custom_helper.stop_speaking()
            self.tts_helper.stop_speaking()
            print("[STOP] 音声を停止しました")
        except Exception as e:
            print(f"音声停止エラー: {e}")
    
    def select_audio_file(self):
        """音声ファイル選択"""
        file_path = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=[
                ("音声ファイル", "*.wav *.mp3 *.ogg"),
                ("WAVファイル", "*.wav"),
                ("MP3ファイル", "*.mp3"),
                ("OGGファイル", "*.ogg"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            self.selected_audio_file.set(f"選択: {os.path.basename(file_path)}")
            self.selected_file_path = file_path
        else:
            self.selected_audio_file.set("")
            self.selected_file_path = None
    
    def add_voice_mapping(self):
        """音声マッピング追加"""
        text = self.add_text.get().strip()
        
        if not text:
            messagebox.showwarning("警告", "テキストを入力してください")
            return
        
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            messagebox.showwarning("警告", "音声ファイルを選択してください")
            return
        
        try:
            success = self.custom_helper.add_voice_file(text, self.selected_file_path)
            if success:
                messagebox.showinfo("成功", f"音声マッピングを追加しました: '{text}'")
                self.add_text.set("")
                self.selected_audio_file.set("")
                self.selected_file_path = None
                self.refresh_voice_list()
            else:
                messagebox.showerror("エラー", "音声マッピングの追加に失敗しました")
                
        except Exception as e:
            messagebox.showerror("エラー", f"音声マッピング追加エラー: {e}")
    
    def delete_selected_voice(self):
        """選択された音声マッピングを削除"""
        selection = self.voice_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除する項目を選択してください")
            return
        
        item = self.voice_tree.item(selection[0])
        text = item['values'][0]
        filename = item['values'][1]
        
        result = messagebox.askyesno("確認", f"'{text}' の音声マッピングを削除しますか？")
        if result:
            try:
                # マッピングから削除
                if text in self.custom_helper.voice_mapping:
                    del self.custom_helper.voice_mapping[text]
                    self.custom_helper._save_voice_mapping()
                
                # ファイルも削除
                file_path = os.path.join(self.custom_helper.voice_folder, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                messagebox.showinfo("成功", f"音声マッピングを削除しました: '{text}'")
                self.refresh_voice_list()
                
            except Exception as e:
                messagebox.showerror("エラー", f"削除エラー: {e}")
    
    def open_voice_folder(self):
        """音声フォルダを開く"""
        try:
            import subprocess
            folder_path = os.path.abspath(self.custom_helper.voice_folder)
            os.makedirs(folder_path, exist_ok=True)
            subprocess.run(f'explorer "{folder_path}"')
        except Exception as e:
            messagebox.showerror("エラー", f"フォルダを開けませんでした: {e}")
    
    def save_settings(self):
        """設定を保存"""
        try:
            # 設定ファイルに保存（今後の実装）
            settings = {
                "voice_engine": self.engine_var.get(),
                "test_text": self.test_text.get()
            }
            
            with open("voice_settings.json", "w", encoding="utf-8") as f:
                import json
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "設定を保存しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"設定保存エラー: {e}")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
=== 音声設定ヘルプ ===

【カスタム音声について】
- 事前に録音した音声ファイルを使用して読み上げ
- WAV形式推奨（MP3、OGGも対応）
- 1-5秒程度の短い音声が最適
- よく読み取られる文字や単語を登録すると効果的

【使用方法】
1. テキスト欄に読み上げたい文字を入力
2. 音声ファイルを選択して追加
3. 音声テストで動作確認
4. OCRアプリで実際に使用

【推奨登録文字】
- 数字: 0, 1, 2, 3... 
- 挨拶: こんにちは、ありがとうございます
- よく使う単語: 価格、円、商品名など

【注意事項】
- 音声ファイルは custom_voices フォルダに保存されます
- ファイルサイズが大きいと読み込みに時間がかかります
- カスタム音声がない場合は標準音声で再生されます

==============================="""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("ヘルプ")
        help_window.geometry("500x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, font=("MS Gothic", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="閉じる", command=help_window.destroy).pack(pady=5)
    
    def close_window(self):
        """ウィンドウを閉じる"""
        self.stop_voice()
        self.root.destroy()
    
    def run(self):
        """GUIを実行"""
        self.root.mainloop()

def open_voice_config():
    """音声設定画面を開く"""
    try:
        app = VoiceConfigGUI()
        app.run()
    except Exception as e:
        import traceback
        print(f"音声設定GUI起動エラー: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    open_voice_config()