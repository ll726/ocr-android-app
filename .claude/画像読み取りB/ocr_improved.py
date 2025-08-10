import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import sys
import os

# Tesseract設定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def enhance_image_advanced(image_np):
    """
    OCR精度向上のための高度な画像前処理
    
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
    
    # ノイズ除去
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # ガウシアンブラーでわずかに平滑化
    blurred = cv2.GaussianBlur(denoised, (1, 1), 0)
    
    # コントラスト強化（適応的）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_enhanced = clahe.apply(blurred)
    
    # シャープニング
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(contrast_enhanced, -1, kernel)
    
    # 適応的二値化（複数手法を試行）
    binary1 = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    binary2 = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # 大津の二値化も試行
    _, binary3 = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary1, binary2, binary3

def ocr_with_multiple_configs(image_path):
    """
    複数の設定でOCRを実行し、最も信頼度の高い結果を返す
    
    Args:
        image_path (str): 画像ファイルのパス
    
    Returns:
        str: 抽出されたテキスト
    """
    try:
        # 画像を開く
        img = Image.open(image_path)
        cv_img = np.array(img)
        
        # 複数の前処理を適用
        binary1, binary2, binary3 = enhance_image_advanced(cv_img)
        
        # 複数のTesseract設定
        configs = [
            '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
            '--psm 7',
            '--psm 8',
            '--psm 6',
            '--psm 13'
        ]
        
        results = []
        
        # 各前処理と各設定の組み合わせを試行
        for i, binary in enumerate([binary1, binary2, binary3]):
            pil_img = Image.fromarray(binary)
            
            for j, config in enumerate(configs):
                try:
                    # データと信頼度を取得
                    data = pytesseract.image_to_data(pil_img, lang='jpn', config=config, output_type=pytesseract.Output.DICT)
                    
                    # 信頼度の平均を計算
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # テキストを取得
                    text = pytesseract.image_to_string(pil_img, lang='jpn', config=config).strip()
                    
                    if text and avg_confidence > 30:  # 最低信頼度30%
                        results.append((text, avg_confidence, i, j))
                        
                except Exception as e:
                    continue
        
        # 最も信頼度の高い結果を選択
        if results:
            best_result = max(results, key=lambda x: x[1])
            print(f"最適設定: 前処理{best_result[2]}, 設定{best_result[3]}, 信頼度: {best_result[1]:.1f}%")
            return best_result[0]
        else:
            # フォールバック: 元の方法
            pil_img = Image.fromarray(binary1)
            return pytesseract.image_to_string(pil_img, lang='jpn')
        
    except Exception as e:
        print(f"OCR処理中にエラーが発生しました: {e}")
        return ""

def test_ocr_accuracy():
    """OCR精度をテストする"""
    # エンコーディング設定
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    test_image = "test_image_jp.png"
    
    print("=== OCR精度テスト ===")
    
    # 元の方法
    print("1. 元の方法:")
    img = Image.open(test_image)
    cv_img = np.array(img)
    if len(cv_img.shape) == 3:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv_img.copy()
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil_img = Image.fromarray(binary)
    original_result = pytesseract.image_to_string(pil_img, lang='jpn')
    print(f"結果: {original_result.strip()}")
    
    print("\n2. 改良版:")
    improved_result = ocr_with_multiple_configs(test_image)
    print(f"結果: {improved_result}")
    
    return improved_result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = ocr_with_multiple_configs(sys.argv[1])
        print("OCR結果:")
        print(result)
    else:
        test_ocr_accuracy()