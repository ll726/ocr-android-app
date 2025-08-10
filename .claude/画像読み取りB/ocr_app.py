import pytesseract
from PIL import Image, ImageEnhance
import sys
import os
import cv2  # OpenCVをインポート
import numpy as np

# --- 設定 ---
# ここにTesseract-OCRのインストールパスを指定してください
# 例: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def ocr_image(image_path):
    """
    画像ファイルから文字を読み取り、テキストを返す

    Args:
        image_path (str): 画像ファイルのパス

    Returns:
        str: 抽出されたテキスト
    """
    try:
        # 画像を開く
        img = Image.open(image_path)
        
        # PIL ImageをOpenCV形式に変換
        cv_img = np.array(img)
        
        # 高精度前処理を適用
        processed_img_np = enhance_image_for_ocr(cv_img)
        
        # NumPy配列からPIL Imageに変換
        processed_img = Image.fromarray(processed_img_np)

        # OCRの実行（日本語を指定）
        text = pytesseract.image_to_string(processed_img, lang='jpn')
        
        return text

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {image_path}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"OCR処理中にエラーが発生しました: {e}", file=sys.stderr)
        return ""

def enhance_image_for_ocr(image_np):
    """
    OCR精度向上のためのシンプルな画像前処理
    
    Args:
        image_np (numpy.ndarray): 入力画像
    
    Returns:
        numpy.ndarray: 前処理済み画像
    """
    # グレースケール化
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_np.copy()
    
    # 大津の二値化（元の方法を使用）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary

def ocr_frame(frame_np):
    """
    OpenCVのフレーム（NumPy配列）から文字を読み取り、テキストを返す

    Args:
        frame_np (numpy.ndarray): OpenCVのフレーム（NumPy配列）

    Returns:
        str: 抽出されたテキスト
    """
    try:
        # 高精度前処理を適用
        processed_frame = enhance_image_for_ocr(frame_np)

        # NumPy配列からPIL Imageに変換
        pil_img = Image.fromarray(processed_frame)

        # シンプルなOCR実行（日本語を指定）
        text = pytesseract.image_to_string(pil_img, lang='jpn')
        
        return text

    except Exception as e:
        print(f"OCRフレーム処理中にエラーが発生しました: {e}", file=sys.stderr)
        return ""

def capture_and_ocr_from_camera():
    """
    カメラを起動し、キャプチャした画像から文字を読み取る
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("エラー: カメラを開けません。")
        return

    print("カメラを起動しました。")
    print("SPACEキーを押すとOCRを実行します。")
    print("'q'キーを押すと終了します。")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("エラー: フレームをキャプチャできません。")
            break

        # 画面にフレームを表示
        cv2.imshow('Camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # 'q'キーが押されたら
            break
        elif key == ord(' '):  # SPACEキーが押されたら
            # ウィンドウタイトルを変更して処理中であることを示す
            cv2.setWindowTitle('Camera', 'Camera - Processing...')
            print("\n手動キャプチャ: 画像を処理します...")

            # --- 画像のリサイズ処理 ---
            h, w, _ = frame.shape
            resize_w = 1280
            resize_h = int(h * (resize_w / w))
            resized_frame = cv2.resize(frame, (resize_w, resize_h))
            print(f"画像をリサイズしました: ({w}x{h}) -> ({resize_w}x{resize_h})")
            # --------------------------

            # OCRを実行
            print("OCRを実行中...")
            extracted_text = ocr_frame(resized_frame) # ocr_frameを呼び出す
            print("OCR処理が完了しました。")

            print("--- 読み取り結果 ---")
            if extracted_text and not extracted_text.isspace():
                print(extracted_text)
            else:
                print("文字は検出されませんでした。")
            print("--------------------")

            # 処理が完了したらウィンドウタイトルを元に戻す
            cv2.setWindowTitle('Camera', 'Camera')

    # 後処理
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 引数に応じて処理を分岐
    if len(sys.argv) > 1 and sys.argv[1] == "camera":
        capture_and_ocr_from_camera()
    elif len(sys.argv) > 1:
        input_path = sys.argv[1]
        # OCRを実行して結果を表示
        extracted_text = ocr_image(input_path)
        print(extracted_text)
    else:
        print("使用法:")
        print("  画像ファイルから読み取る場合: python ocr_app.py <画像ファイルのパス>")
        print("  カメラから読み取る場合:      python ocr_app.py camera")
        sys.exit(1)
