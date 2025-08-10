import os
import subprocess
import tempfile
import pyperclip
from datetime import datetime
import win32com.client

class TextOutputHelper:
    """
    OCR結果をメモ帳・Word・テキストファイルに出力するヘルパークラス
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def save_to_notepad(self, text, title="OCR結果"):
        """
        テキストをメモ帳で開く
        
        Args:
            text (str): 出力するテキスト
            title (str): ファイル名のタイトル部分
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title}_{timestamp}.txt"
            filepath = os.path.join(self.temp_dir, filename)
            
            # テキストファイルを作成
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== {title} ===\n")
                f.write(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write("=" * 40 + "\n\n")
                f.write(text)
                f.write("\n\n" + "=" * 40)
                f.write(f"\nOCR Camera App で生成")
            
            # メモ帳で開く
            subprocess.Popen(['notepad.exe', filepath])
            print(f"[OK] メモ帳で開きました: {filename}")
            return filepath
            
        except Exception as e:
            print(f"メモ帳出力エラー: {e}")
            return None
    
    def save_to_word(self, text, title="OCR結果"):
        """
        テキストをWordドキュメントで開く
        
        Args:
            text (str): 出力するテキスト
            title (str): ドキュメントのタイトル
        """
        try:
            # Word アプリケーションを起動
            word_app = win32com.client.Dispatch("Word.Application")
            word_app.Visible = True
            
            # 新しいドキュメントを作成
            doc = word_app.Documents.Add()
            
            # タイトルを追加
            title_text = f"{title}\n"
            title_range = doc.Range()
            title_range.InsertAfter(title_text)
            title_range.Font.Bold = True
            title_range.Font.Size = 16
            
            # 日時を追加
            datetime_text = f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
            datetime_range = doc.Range(len(title_text), len(title_text))
            datetime_range.InsertAfter(datetime_text)
            datetime_range.Font.Size = 10
            datetime_range.Font.Italic = True
            
            # 区切り線
            separator = "\n" + "=" * 50 + "\n\n"
            separator_pos = len(title_text) + len(datetime_text)
            separator_range = doc.Range(separator_pos, separator_pos)
            separator_range.InsertAfter(separator)
            
            # メインテキストを追加
            main_text_pos = separator_pos + len(separator)
            main_range = doc.Range(main_text_pos, main_text_pos)
            main_range.InsertAfter(text)
            main_range.Font.Size = 12
            main_range.Font.Name = "游ゴシック"
            
            # フッターを追加
            footer_text = f"\n\n{'-' * 50}\nOCR Camera App で生成"
            footer_pos = main_text_pos + len(text)
            footer_range = doc.Range(footer_pos, footer_pos)
            footer_range.InsertAfter(footer_text)
            footer_range.Font.Size = 8
            footer_range.Font.Color = 0x808080  # グレー
            
            print(f"[OK] Wordドキュメントを開きました")
            return True
            
        except Exception as e:
            print(f"Word出力エラー: {e}")
            print("Wordがインストールされていない可能性があります")
            return False
    
    def copy_to_clipboard(self, text):
        """
        テキストをクリップボードにコピー
        
        Args:
            text (str): コピーするテキスト
        """
        try:
            pyperclip.copy(text)
            print(f"[OK] クリップボードにコピーしました ({len(text)}文字)")
            return True
        except Exception as e:
            print(f"クリップボードコピーエラー: {e}")
            return False
    
    def save_to_text_file(self, text, title="OCR結果", save_dir=None):
        """
        テキストファイルとして保存
        
        Args:
            text (str): 保存するテキスト
            title (str): ファイル名のタイトル部分
            save_dir (str): 保存ディレクトリ（Noneなら現在のディレクトリ）
        """
        try:
            if save_dir is None:
                save_dir = os.getcwd()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title}_{timestamp}.txt"
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== {title} ===\n")
                f.write(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write(f"保存場所: {filepath}\n")
                f.write("=" * 40 + "\n\n")
                f.write(text)
                f.write("\n\n" + "=" * 40)
                f.write(f"\nOCR Camera App で生成")
            
            print(f"[OK] テキストファイルを保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"テキストファイル保存エラー: {e}")
            return None
    
    def save_to_excel(self, text, title="OCR結果"):
        """
        テキストをExcelワークシートに出力
        
        Args:
            text (str): 出力するテキスト
            title (str): ワークシートのタイトル
        """
        try:
            # Excel アプリケーションを起動
            excel_app = win32com.client.Dispatch("Excel.Application")
            excel_app.Visible = True
            
            # 新しいワークブックを作成
            workbook = excel_app.Workbooks.Add()
            worksheet = workbook.ActiveSheet
            
            # タイトルを設定
            worksheet.Cells(1, 1).Value = title
            worksheet.Cells(1, 1).Font.Bold = True
            worksheet.Cells(1, 1).Font.Size = 14
            
            # 日時を設定
            worksheet.Cells(2, 1).Value = f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"
            worksheet.Cells(2, 1).Font.Size = 10
            
            # テキストを行ごとに分割してセルに配置
            lines = text.split('\n')
            for i, line in enumerate(lines, start=4):  # 4行目から開始
                worksheet.Cells(i, 1).Value = line
                worksheet.Cells(i, 1).WrapText = True  # テキストの折り返し
            
            # 列幅を調整
            worksheet.Columns(1).AutoFit()
            if worksheet.Columns(1).ColumnWidth > 50:
                worksheet.Columns(1).ColumnWidth = 50
            
            print(f"[OK] Excelワークシートを開きました")
            return True
            
        except Exception as e:
            print(f"Excel出力エラー: {e}")
            print("Excelがインストールされていない可能性があります")
            return False
    
    def open_with_default_editor(self, text, title="OCR結果"):
        """
        システムのデフォルトテキストエディタで開く
        
        Args:
            text (str): 開くテキスト
            title (str): ファイル名のタイトル
        """
        try:
            filepath = self.save_to_text_file(text, title)
            if filepath:
                # デフォルトアプリケーションで開く
                os.startfile(filepath)
                print(f"[OK] デフォルトエディタで開きました")
                return filepath
            return None
            
        except Exception as e:
            print(f"デフォルトエディタ起動エラー: {e}")
            return None

def show_text_output_menu():
    """テキスト出力のメニューを表示"""
    menu = """
=== テキスト出力メニュー ===
1. メモ帳で開く
2. Wordドキュメントで開く  
3. クリップボードにコピー
4. テキストファイルに保存
5. Excelワークシートで開く
6. デフォルトエディタで開く
===========================
"""
    print(menu)

# 便利関数
def quick_output_text(text, output_type="notepad", title="OCR結果"):
    """
    テキストを指定された形式で素早く出力
    
    Args:
        text (str): 出力するテキスト
        output_type (str): 出力形式 ("notepad", "word", "clipboard", "file", "excel", "default")
        title (str): タイトル
    """
    helper = TextOutputHelper()
    
    if output_type.lower() == "notepad":
        return helper.save_to_notepad(text, title)
    elif output_type.lower() == "word":
        return helper.save_to_word(text, title)
    elif output_type.lower() == "clipboard":
        return helper.copy_to_clipboard(text)
    elif output_type.lower() == "file":
        return helper.save_to_text_file(text, title)
    elif output_type.lower() == "excel":
        return helper.save_to_excel(text, title)
    elif output_type.lower() == "default":
        return helper.open_with_default_editor(text, title)
    else:
        print(f"不明な出力形式: {output_type}")
        return None

if __name__ == "__main__":
    # テスト実行
    test_text = """これはテストテキストです。
OCRで読み取った文字をメモ帳やWordに出力するテストを行います。

日本語のテキストもしっかりと出力されることを確認します。
改行や特殊文字も含めてテストしています。

テスト完了。"""
    
    print("テキスト出力機能のテスト")
    show_text_output_menu()
    
    # メモ帳テスト
    quick_output_text(test_text, "notepad", "テスト結果")