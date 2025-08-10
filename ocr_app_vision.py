import pytesseract
from PIL import Image
import sys
import os
import cv2
import numpy as np
import json

# Google Vision API imports
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    print("Google Cloud Vision not installed. Using Tesseract only.")

# --- 設定 ---
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Google Vision API設定
GOOGLE_KEY_PATH = "google-vision-key.json"

def setup_google_vision():
    """Google Vision APIの設定を行う"""
    if not GOOGLE_VISION_AVAILABLE:
        return None
    
    key_path = os.path.join(os.path.dirname(__file__), GOOGLE_KEY_PATH)
    if not os.path.exists(key_path):
        return None
    
    # 環境変数を設定
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
    
    try:
        client = vision.ImageAnnotatorClient()
        return client
    except Exception as e:
        print(f"Google Vision API setup error: {e}")
        return None

def ocr_with_google_vision(image_path):
    """Google Vision APIを使用したOCR"""
    client = setup_google_vision()
    if not client:
        return None
    
    try:
        # 画像を読み込み
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # テキスト検出を実行
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        else:
            return ""
    
    except Exception as e:
        print(f"Google Vision API error: {e}")
        return None

def ocr_frame_with_google_vision(frame_np):
    """Google Vision APIを使用したフレームOCR"""
    client = setup_google_vision()
    if not client:
        return None
    
    try:
        # NumPy配列を画像バイトに変換
        _, encoded_image = cv2.imencode('.png', frame_np)
        content = encoded_image.tobytes()
        
        image = vision.Image(content=content)
        
        # テキスト検出を実行
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        else:
            return ""
    
    except Exception as e:
        print(f"Google Vision API frame error: {e}")
        return None

def enhance_image_for_ocr(image_np):
    """OCR精度向上のためのシンプルな画像前処理"""
    # グレースケール化
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_np.copy()
    
    # 大津の二値化（元の方法を使用）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary

def ocr_image(image_path):
    """画像ファイルから文字を読み取り、テキストを返す"""
    try:
        # まずGoogle Vision APIを試行
        if GOOGLE_VISION_AVAILABLE:
            google_result = ocr_with_google_vision(image_path)
            if google_result is not None:
                print("[OK] Google Vision API を使用")
                return google_result
        
        print("[OK] Tesseract を使用")
        # Google Vision APIが使えない場合はTesseractを使用
        img = Image.open(image_path)
        cv_img = np.array(img)
        processed_img_np = enhance_image_for_ocr(cv_img)
        processed_img = Image.fromarray(processed_img_np)
        text = pytesseract.image_to_string(processed_img, lang='jpn')
        return text

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {image_path}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"OCR処理中にエラーが発生しました: {e}", file=sys.stderr)
        return ""

def ocr_frame(frame_np):
    """OpenCVのフレーム（NumPy配列）から文字を読み取り、テキストを返す"""
    try:
        # まずGoogle Vision APIを試行
        if GOOGLE_VISION_AVAILABLE:
            google_result = ocr_frame_with_google_vision(frame_np)
            if google_result is not None:
                print("[OK] Google Vision API を使用")
                return google_result
        
        print("[OK] Tesseract を使用")
        # Google Vision APIが使えない場合はTesseractを使用
        processed_frame = enhance_image_for_ocr(frame_np)
        pil_img = Image.fromarray(processed_frame)
        text = pytesseract.image_to_string(pil_img, lang='jpn')
        return text

    except Exception as e:
        print(f"OCRフレーム処理中にエラーが発生しました: {e}", file=sys.stderr)
        return ""

def capture_and_ocr_from_camera():
    """カメラを起動し、キャプチャした画像から文字を読み取る"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("エラー: カメラを開けません。")
        return

    print("カメラを起動しました。")
    print("SPACEキーを押すとOCRを実行します。")
    print("'q'キーを押すと終了します。")
    
    # Google Vision APIの状態を表示
    if GOOGLE_VISION_AVAILABLE and setup_google_vision():
        print("[OK] Google Vision API 利用可能（高精度モード）")
    else:
        print("[OK] Tesseract モード（標準精度）")

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
            extracted_text = ocr_frame(resized_frame)
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
    # 起動時にGoogle Vision APIの状態を確認
    print("=== OCR アプリ (Google Vision API対応版) ===")
    if GOOGLE_VISION_AVAILABLE:
        if os.path.exists(GOOGLE_KEY_PATH):
            print("[OK] Google Vision API設定ファイル検出")
        else:
            print("[WARNING] Google Vision APIキーファイルが見つかりません")
            print(f"  {GOOGLE_KEY_PATH} を配置してください")
    else:
        print("[WARNING] Google Vision APIライブラリが見つかりません")
        print("  setup_google_vision.bat を実行してください")
    print("=" * 45)
    
    # 引数に応じて処理を分岐
    if len(sys.argv) > 1 and sys.argv[1] == "camera":
        capture_and_ocr_from_camera()
    elif len(sys.argv) > 1:
        input_path = sys.argv[1]
        extracted_text = ocr_image(input_path)
        print(extracted_text)
    else:
        print("使用法:")
        print("  画像ファイルから読み取る場合: python ocr_app_vision.py <画像ファイルのパス>")
        print("  カメラから読み取る場合:      python ocr_app_vision.py camera")
        sys.exit(1)