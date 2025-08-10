#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android版OCRアプリのビルド環境セットアップスクリプト
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def run_command(command, description):
    """コマンドを実行して結果を表示"""
    print(f"\n[実行中] {description}")
    print(f"コマンド: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 成功")
            if result.stdout:
                print(f"出力: {result.stdout.strip()}")
        else:
            print("✗ エラー")
            if result.stderr:
                print(f"エラー: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"✗ 実行エラー: {e}")
        return False

def check_system_requirements():
    """システム要件をチェック"""
    print_section("システム要件チェック")
    
    # Python バージョンチェック
    python_version = sys.version_info
    print(f"Python バージョン: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major != 3 or python_version.minor < 8:
        print("⚠️  Python 3.8以上を推奨します")
    else:
        print("✓ Python バージョンOK")
    
    # OS チェック
    os_name = platform.system()
    print(f"OS: {os_name}")
    
    if os_name == "Windows":
        print("✓ Windows環境（WSL推奨）")
    elif os_name == "Linux":
        print("✓ Linux環境（最適）")
    elif os_name == "Darwin":
        print("✓ macOS環境")
    
    # Git チェック
    if run_command("git --version", "Git確認"):
        print("✓ Git利用可能")
    else:
        print("⚠️  Gitのインストールを推奨")

def install_buildozer():
    """Buildozerをインストール"""
    print_section("Buildozer環境構築")
    
    # システムの依存関係インストール (Ubuntu/Debian用)
    if platform.system() == "Linux":
        dependencies = [
            "python3-pip",
            "build-essential", 
            "git",
            "python3-dev",
            "ffmpeg",
            "libsdl2-dev",
            "libsdl2-image-dev",
            "libsdl2-mixer-dev",
            "libsdl2-ttf-dev",
            "libportmidi-dev",
            "libswscale-dev",
            "libavformat-dev",
            "libavcodec-dev",
            "zlib1g-dev",
            "libgstreamer1.0",
            "gstreamer1.0-plugins-base",
            "gstreamer1.0-plugins-good"
        ]
        
        print("システム依存関係をインストール中...")
        for dep in dependencies:
            run_command(f"sudo apt-get install -y {dep}", f"{dep}をインストール")
    
    # Buildozer インストール
    run_command("pip install --upgrade pip", "pipをアップグレード")
    run_command("pip install buildozer", "Buildozerをインストール")
    run_command("pip install cython", "Cythonをインストール")

def setup_android_sdk():
    """Android SDK セットアップ"""
    print_section("Android SDK セットアップ")
    
    home_dir = Path.home()
    android_home = home_dir / ".android"
    
    print(f"Android SDK パス: {android_home}")
    
    if not android_home.exists():
        print("Android SDKがインストールされていません")
        print("以下の手順でインストールしてください:")
        print("1. Android Studio をインストール")
        print("2. SDK Manager で必要なコンポーネントをインストール") 
        print("3. 環境変数 ANDROID_HOME を設定")
    else:
        print("✓ Android SDK が見つかりました")

def create_demo_files():
    """デモファイルを作成"""
    print_section("デモファイル作成")
    
    # アイコンファイル（仮）
    icon_content = '''
# アイコンファイル用のプレースホルダー
# 実際にはPNG画像ファイルを使用してください
# サイズ: 512x512 推奨
'''
    
    with open("icon_placeholder.txt", "w", encoding="utf-8") as f:
        f.write(icon_content)
    
    print("✓ アイコンプレースホルダーを作成")
    
    # テスト用画像
    test_image_info = '''
テスト用画像の準備:
1. test_image.jpg - OCRテスト用の日本語テキスト画像
2. 解像度: 800x600 程度
3. 日本語テキストが明確に読める画像
'''
    
    with open("test_images_info.txt", "w", encoding="utf-8") as f:
        f.write(test_image_info)
    
    print("✓ テスト画像情報を作成")

def build_debug_apk():
    """デバッグ用APKをビルド"""
    print_section("デバッグAPKビルド")
    
    print("デバッグAPKをビルドします（時間がかかります）...")
    
    if run_command("buildozer android debug", "デバッグAPKビルド"):
        print("✓ デバッグAPKのビルドが完了しました")
        print("APKファイル: ./bin/ocrapp-1.0-debug.apk")
    else:
        print("✗ APKビルドに失敗しました")
        print("エラーログを確認してください")

def show_next_steps():
    """次のステップを表示"""
    print_section("次のステップ")
    
    next_steps = """
1. デバッグAPKのテスト:
   - Android端末にAPKをインストール
   - adb install bin/ocrapp-1.0-debug.apk

2. リリースAPKの作成:
   - キーストアを作成
   - buildozer android release

3. Google Play Consoleでの公開:
   - Google Play Developer アカウントが必要
   - AABファイル（Android App Bundle）を推奨

4. アプリのカスタマイズ:
   - アイコン画像を追加 (icon.png)
   - アプリ名・パッケージ名を変更
   - 権限・機能を調整

5. テストの実施:
   - OCR機能のテスト
   - カメラ機能のテスト  
   - 音声機能のテスト
"""
    
    print(next_steps)

def main():
    """メイン処理"""
    print("Android版OCRアプリ ビルド環境セットアップ")
    print("=" * 50)
    
    # システム要件チェック
    check_system_requirements()
    
    choice = input("\n続行しますか？ (y/N): ").strip().lower()
    if choice not in ['y', 'yes']:
        print("セットアップを中止しました")
        return
    
    # Buildozer環境構築
    install_buildozer()
    
    # Android SDK セットアップ
    setup_android_sdk()
    
    # デモファイル作成
    create_demo_files()
    
    # ビルド実行するか確認
    build_choice = input("\nデバッグAPKをビルドしますか？ (y/N): ").strip().lower()
    if build_choice in ['y', 'yes']:
        build_debug_apk()
    
    # 次のステップ表示
    show_next_steps()
    
    print("\n✅ セットアップ完了！")

if __name__ == "__main__":
    main()