import cv2
import sys
import os
from ocr_app_vision import ocr_frame
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from mercari_price_checker import get_mercari_prices, analyze_prices, format_price_info
from mercari_real_scraper import get_real_mercari_prices
from mercari_improved_scraper import get_real_mercari_prices_improved
from rakuten_api_client import get_rakuten_prices, analyze_rakuten_prices, format_rakuten_price_info
from simple_price_checker import get_simple_prices, analyze_simple_prices, format_simple_price_info
from bookoff_scraper import get_bookoff_prices, analyze_bookoff_prices, format_bookoff_price_info
from rakuma_scraper import get_rakuma_prices, analyze_rakuma_prices, format_rakuma_price_info
from text_output_helper import TextOutputHelper, quick_output_text
from text_to_speech_helper import TextToSpeechHelper, quick_speak
# from translation_helper import TranslationHelper, format_translation_result
from summary_helper import SummaryHelper, format_summary_result, quick_summarize
from ai_summary_helper import AISummaryHelper, format_ai_summary_result, quick_ai_summarize
from real_ai_summary_helper import RealAISummaryHelper, format_real_ai_summary_result

def draw_japanese_text(img, text, position):
    """日本語テキストを画像に描画する関数"""
    try:
        # OpenCV画像をPIL画像に変換
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # デフォルトフォントを使用（日本語対応）
        try:
            # Windowsの日本語フォントを試す
            font = ImageFont.truetype("msgothic.ttc", 20)
        except:
            try:
                font = ImageFont.truetype("NotoSansCJK-Regular.ttc", 20)
            except:
                # デフォルトフォントを使用
                font = ImageFont.load_default()
        
        # テキストを描画（緑色）
        draw.text(position, f"結果: {text}", font=font, fill=(0, 255, 0))
        
        # PIL画像をOpenCV画像に戻す
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_cv
    except Exception as e:
        print(f"フォント描画エラー: {e}")
        # エラーの場合は英語で表示
        cv2.putText(img, f"Result: {text}", position, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        return img

def simple_camera_ocr():
    """シンプルなカメラOCRアプリ"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("エラー: カメラを開けません。")
        return

    print("=== カメラOCR + 価格検索 ===")
    print("カメラを起動しました。")
    print("SPACEキー: OCR実行")
    print("Pキー: 価格検索（サンプル版）")
    print("Rキー: メルカリ価格検索")
    print("Tキー: 楽天市場価格検索")
    print("Sキー: 簡単価格チェック（APIキー不要）")
    print("Bキー: ブックオフ価格検索")
    print("Lキー: ラクマSOLD価格検索")
    print("--- テキスト出力・読み上げ・要約 ---")
    print("Nキー: メモ帳に出力")
    print("Wキー: Wordに出力") 
    print("Cキー: クリップボードにコピー")
    print("Vキー: 音声読み上げ")
    print("Uキー: 基本要約")
    print("Aキー: AI高度要約")
    print("Iキー: 真のAI要約 (API)")
    print("'q'キー: 終了")
    print("=============================")
    
    # 認識結果を保存する変数
    last_ocr_result = ""
    last_summary_result = ""  # 要約結果を保存
    ocr_history = []
    
    # 音声合成エンジンを初期化
    tts_helper = TextToSpeechHelper()
    
    # 翻訳エンジンを初期化
    # translator = TranslationHelper()
    
    # 要約エンジンを初期化
    summary_helper = SummaryHelper()
    ai_summary_helper = AISummaryHelper()
    real_ai_summary_helper = RealAISummaryHelper()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("エラー: フレームをキャプチャできません。")
            break

        # フレームにOCR結果を描画
        display_frame = frame.copy()
        
        # 最新のOCR結果を画面上に表示
        if last_ocr_result:
            # 背景となる矩形を描画
            cv2.rectangle(display_frame, (10, 10), (620, 100), (0, 0, 0), -1)
            cv2.rectangle(display_frame, (10, 10), (620, 100), (255, 255, 255), 2)
            
            # PILを使って日本語テキストを描画
            display_frame = draw_japanese_text(display_frame, last_ocr_result, (20, 30))
        
        # 操作説明を画面下部に表示
        h, w = display_frame.shape[:2]
        cv2.rectangle(display_frame, (10, h-60), (w-10, h-10), (0, 0, 0), -1)
        # 2行で表示
        cv2.putText(display_frame, "SPACE: OCR | P: Sample | R: Mercari | T: Rakuten | S: Simple | B: BookOff | L: Rakuma", 
                   (2, h-45), cv2.FONT_HERSHEY_SIMPLEX, 0.22, (255, 255, 255), 1)
        cv2.putText(display_frame, "N: Notepad | W: Word | C: Copy | V: Voice | U/A/I: Summary | Q: Quit", 
                   (2, h-25), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
        
        # フレームを表示
        cv2.imshow('Simple OCR Camera', display_frame)

        key = cv2.waitKey(30) & 0xFF  # waitKeyの時間を長くして確実にキーを捕捉
        if key == ord('q'):
            print("終了します...")
            break
        elif key == 32:  # SPACEキーのコード
            print("\n--- OCR実行中 ---")
            try:
                # フレームサイズを小さくして処理を軽量化
                h, w, _ = frame.shape
                print(f"元の画像サイズ: {w}x{h}")
                
                if w > 800:
                    scale = 800 / w
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    small_frame = cv2.resize(frame, (new_w, new_h))
                    print(f"リサイズ後: {new_w}x{new_h}")
                else:
                    small_frame = frame
                    print("リサイズなし")
                
                # デバッグ用：処理前の画像を一時保存
                cv2.imwrite("debug_capture.png", small_frame)
                print("デバッグ画像を保存: debug_capture.png")
                
                # OCR実行
                print("OCR処理開始...")
                text = ocr_frame(small_frame)
                print("OCR処理完了")
                
                print("--- 読み取り結果 ---")
                print(f"テキスト長: {len(text) if text else 0}")
                if text and not text.isspace():
                    result_text = text.strip()
                    print(f"結果: '{result_text}'")
                    # 画面表示用に結果を保存
                    last_ocr_result = result_text
                    last_summary_result = ""  # 新しいOCR実行時に要約をクリア
                    ocr_history.append(result_text)
                    if len(ocr_history) > 10:  # 最新10件を保持
                        ocr_history.pop(0)
                else:
                    print("文字は検出されませんでした。")
                    last_ocr_result = "No text detected"
                    last_summary_result = ""  # 要約もクリア
                print("------------------")
                
            except Exception as e:
                print(f"OCR処理エラー: {e}")
                import traceback
                traceback.print_exc()
                
        elif key == ord('p') or key == ord('P'):  # Pキーが押されたら価格検索（サンプル版）
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 価格検索実行（サンプル版）: {last_ocr_result} ---")
                try:
                    prices = get_mercari_prices(last_ocr_result, max_results=5)
                    analysis = analyze_prices(prices)
                    price_info = format_price_info(analysis)
                    print(price_info)
                except Exception as e:
                    print(f"価格検索エラー: {e}")
            else:
                print("\n--- 価格検索（サンプル版） ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("----------------------------")
                
        elif key == ord('r') or key == ord('R'):  # Rキーが押されたら実際のメルカリ価格検索
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 改良版メルカリ価格検索: {last_ocr_result} ---")
                print("複数の方法でデータ取得を試行します...")
                try:
                    real_prices = get_real_mercari_prices_improved(last_ocr_result, max_results=5)
                    analysis = analyze_prices(real_prices)
                    price_info = format_price_info(analysis)
                    print(price_info)
                except Exception as e:
                    print(f"実価格検索エラー: {e}")
            else:
                print("\n--- 改良版メルカリ価格検索 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-----------------------------")
                
        elif key == ord('t') or key == ord('T'):  # Tキーが押されたら楽天市場価格検索
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 楽天市場価格検索: {last_ocr_result} ---")
                print("楽天市場APIでデータ取得中...")
                try:
                    rakuten_prices = get_rakuten_prices(last_ocr_result, max_results=5)
                    analysis = analyze_rakuten_prices(rakuten_prices)
                    price_info = format_rakuten_price_info(analysis)
                    print(price_info)
                except Exception as e:
                    print(f"楽天価格検索エラー: {e}")
            else:
                print("\n--- 楽天市場価格検索 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-------------------------")
                
        elif key == ord('s') or key == ord('S'):  # Sキーが押されたら簡単価格チェック
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 簡単価格チェック: {last_ocr_result} ---")
                print("複数サイトから価格情報を収集中...")
                try:
                    simple_prices = get_simple_prices(last_ocr_result, max_results=5)
                    analysis = analyze_simple_prices(simple_prices)
                    price_info = format_simple_price_info(analysis)
                    print(price_info)
                except Exception as e:
                    print(f"簡単価格検索エラー: {e}")
            else:
                print("\n--- 簡単価格チェック ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-----------------------")
                
        elif key == ord('b') or key == ord('B'):  # Bキーが押されたらブックオフ価格検索
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- ブックオフ価格検索: {last_ocr_result} ---")
                print("ブックオフオンラインで中古価格を検索中...")
                try:
                    bookoff_prices = get_bookoff_prices(last_ocr_result, max_results=5)
                    analysis = analyze_bookoff_prices(bookoff_prices)
                    price_info = format_bookoff_price_info(analysis)
                    print(price_info)
                except Exception as e:
                    print(f"ブックオフ価格検索エラー: {e}")
            else:
                print("\n--- ブックオフ価格検索 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-----------------------")
                
        elif key == ord('l') or key == ord('L'):  # Lキーが押されたらラクマ価格検索
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- ラクマSOLD価格検索: {last_ocr_result} ---")
                print("ラクマで売れた商品の価格を検索中...")
                try:
                    rakuma_prices = get_rakuma_prices(last_ocr_result, max_results=5)
                    analysis = analyze_rakuma_prices(rakuma_prices)
                    price_info = format_rakuma_price_info(analysis)
                    print(price_info)
                except Exception as e:
                    print(f"ラクマ価格検索エラー: {e}")
            else:
                print("\n--- ラクマSOLD価格検索 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-------------------------")
                
        elif key == ord('n') or key == ord('N'):  # Nキーでメモ帳に出力
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- メモ帳に出力: {last_ocr_result[:30]}... ---")
                try:
                    quick_output_text(last_ocr_result, "notepad", "OCR読み取り結果")
                except Exception as e:
                    print(f"メモ帳出力エラー: {e}")
            else:
                print("\n--- メモ帳出力 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("----------------")
                
        elif key == ord('w') or key == ord('W'):  # WキーでWordに出力
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- Wordに出力: {last_ocr_result[:30]}... ---")
                try:
                    quick_output_text(last_ocr_result, "word", "OCR読み取り結果")
                except Exception as e:
                    print(f"Word出力エラー: {e}")
            else:
                print("\n--- Word出力 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("---------------")
                
        elif key == ord('c') or key == ord('C'):  # Cキーでクリップボードにコピー
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- クリップボードにコピー: {len(last_ocr_result)}文字 ---")
                try:
                    quick_output_text(last_ocr_result, "clipboard")
                except Exception as e:
                    print(f"クリップボードコピーエラー: {e}")
            else:
                print("\n--- クリップボードコピー ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-------------------------")
                
        elif key == ord('v') or key == ord('V'):  # Vキーで音声読み上げ
            # 要約がある場合は要約を、なければ元のOCR結果を読み上げ
            text_to_read = last_summary_result if last_summary_result else last_ocr_result
            text_type = "要約文" if last_summary_result else "元文章"
            
            if text_to_read and text_to_read != "No text detected":
                print(f"\n--- 音声読み上げ ({text_type}): {len(text_to_read)}文字 ---")
                if last_summary_result:
                    print("📄 要約された文章を読み上げます")
                else:
                    print("📄 元の認識文章を読み上げます（要約するには「U」キーを押してください）")
                print("読み上げ中... (読み上げを停止する場合は再度Vキーを押してください)")
                try:
                    if tts_helper.is_speaking:
                        # 読み上げ中なら停止
                        tts_helper.stop_speaking()
                        print("[STOP] 読み上げを停止しました")
                    else:
                        # 読み上げ開始
                        success = tts_helper.speak_text(text_to_read, async_mode=True)
                        if not success:
                            print("音声読み上げに失敗しました")
                except Exception as e:
                    print(f"音声読み上げエラー: {e}")
            else:
                print("\n--- 音声読み上げ ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-------------------")
                
        elif key == ord('u') or key == ord('U'):  # Uキーで文章要約
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 文章要約: {len(last_ocr_result)}文字 ---")
                try:
                    # 要約を実行
                    summary_result = summary_helper.smart_summary(last_ocr_result, 'auto')
                    # 要約結果を保存（音声読み上げ用）
                    last_summary_result = summary_result
                    formatted_result = format_summary_result(summary_result, len(last_ocr_result))
                    print(formatted_result)
                    print("\n💡 ヒント: 要約文を音声で聞くには「V」キーを押してください")
                except Exception as e:
                    print(f"要約エラー: {e}")
            else:
                print("\n--- 基本文章要約 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-------------------")
                
        elif key == ord('a') or key == ord('A'):  # AキーでAI高度要約
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- AI高度要約: {len(last_ocr_result)}文字 ---")
                print("🤖 AI分析中... 文章構造を解析しています...")
                try:
                    # AI要約を実行
                    ai_summary_result = ai_summary_helper.ai_smart_summary(last_ocr_result, 'hybrid')
                    # AI要約結果を保存（音声読み上げ用）
                    last_summary_result = ai_summary_result
                    formatted_result = format_ai_summary_result(ai_summary_result, len(last_ocr_result))
                    print(formatted_result)
                    print("\n💡 ヒント: AI要約文を音声で聞くには「V」キーを押してください")
                except Exception as e:
                    print(f"AI要約エラー: {e}")
            else:
                print("\n--- AI高度要約 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("-----------------")
                
        elif key == ord('i') or key == ord('I'):  # Iキーで真のAI要約
            if last_ocr_result and last_ocr_result != "No text detected":
                # API設定チェック
                if not real_ai_summary_helper.is_configured():
                    print("\n--- 真のAI要約 セットアップ ---")
                    print("🤖 AI API（OpenAI/Gemini/Claude）の設定が必要です。")
                    print("セットアップを実行しますか？ (y/n): ", end="")
                    setup_choice = input().strip().lower()
                    
                    if setup_choice == 'y':
                        if real_ai_summary_helper.setup_wizard():
                            print("✅ セットアップ完了！再度Iキーを押してください。")
                        else:
                            print("❌ セットアップがキャンセルされました。")
                    else:
                        print("真のAI要約を使用するにはAPI設定が必要です。")
                    return
                
                print(f"\n--- 🧠 真のAI要約: {len(last_ocr_result)}文字 ---")
                print("🤖 本物のAI（GPT/Gemini/Claude）で分析中...")
                try:
                    # 真のAI要約を実行
                    result, error = real_ai_summary_helper.get_real_ai_summary(
                        last_ocr_result, 'detailed'
                    )
                    
                    if result:
                        # 真のAI要約結果を保存（音声読み上げ用）
                        last_summary_result = result['summary']
                        formatted_result = format_real_ai_summary_result(result, len(last_ocr_result))
                        print(formatted_result)
                        print("\n💡 ヒント: 真のAI要約文を音声で聞くには「V」キーを押してください")
                    else:
                        print(f"真のAI要約エラー: {error}")
                        print("💡 ヒント: API設定やネットワーク接続を確認してください")
                        
                except Exception as e:
                    print(f"真のAI要約エラー: {e}")
            else:
                print("\n--- 🧠 真のAI要約 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("--------------------")
                
        # elif key == ord('e') or key == ord('E'):  # Eキーで英語翻訳
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 英語翻訳: {last_ocr_result[:30]}... ---")
                try:
                    # 言語を自動検出して英語に翻訳
                    result = translator.translate_text(last_ocr_result, 'en', 'auto')
                    formatted_result = format_translation_result(result)
                    print(formatted_result)
                except Exception as e:
                    print(f"英語翻訳エラー: {e}")
            else:
                print("\n--- 英語翻訳 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("---------------")
                
        # elif key == ord('j') or key == ord('J'):  # Jキーで日本語翻訳
            if last_ocr_result and last_ocr_result != "No text detected":
                print(f"\n--- 日本語翻訳: {last_ocr_result[:30]}... ---")
                try:
                    # 言語を自動検出して日本語に翻訳
                    result = translator.translate_text(last_ocr_result, 'ja', 'auto')
                    formatted_result = format_translation_result(result)
                    print(formatted_result)
                except Exception as e:
                    print(f"日本語翻訳エラー: {e}")
            else:
                print("\n--- 日本語翻訳 ---")
                print("先にSPACEキーでOCRを実行してください。")
                print("----------------")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    simple_camera_ocr()