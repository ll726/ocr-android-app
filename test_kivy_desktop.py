#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kivy版OCRアプリのデスクトップテスト
Android版をビルドする前にデスクトップでテスト
"""

import sys
import os

# 文字エンコーディング設定
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 必要なライブラリの確認
required_packages = [
    'kivy',
    'PIL',
    'cv2', 
    'numpy'
]

missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"[OK] {package} - installed")
    except ImportError:
        missing_packages.append(package)
        print(f"[NG] {package} - not installed")

if missing_packages:
    print(f"\nPlease install the following packages:")
    for pkg in missing_packages:
        if pkg == 'PIL':
            print(f"  pip install Pillow")
        elif pkg == 'cv2':
            print(f"  pip install opencv-python")
        else:
            print(f"  pip install {pkg}")
    
    print(f"\nOr install all at once:")
    print(f"  pip install kivy pillow opencv-python numpy")
    
    sys.exit(1)

print(f"\n[SUCCESS] All required packages are installed")
print(f"Starting Kivy OCR App desktop test...\n")

# メインアプリを起動
try:
    from android_ocr_app import OCRApp
    OCRApp().run()
except Exception as e:
    print(f"[ERROR] App startup error: {e}")
    import traceback
    traceback.print_exc()