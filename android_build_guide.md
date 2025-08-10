# Android版OCRアプリ ビルドガイド

## 📋 概要

Windows版のOCRアプリをAndroid向けに移植したアプリです。
Kivyフレームワークを使用してクロスプラットフォーム対応を実現しています。

## 🎯 主な機能

- **カメラOCR**: カメラで撮影した画像から文字認識
- **ファイルOCR**: ギャラリーの画像から文字認識  
- **音声読み上げ**: OCR結果をTTSで読み上げ
- **日本語対応**: 日本語文字の認識に対応

## 🛠️ ビルド環境構築

### 前提条件

- **OS**: Linux (Ubuntu 20.04+) または macOS推奨
- **Python**: 3.8以上
- **メモリ**: 8GB以上推奨
- **ストレージ**: 20GB以上の空き容量

### 自動セットアップ（推奨）

```bash
python setup_android_build.py
```

### 手動セットアップ

#### 1. システム依存関係のインストール

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3-pip build-essential git python3-dev ffmpeg \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    libgstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

**macOS:**
```bash
brew install python3 git
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
```

#### 2. Pythonパッケージのインストール

```bash
pip install --upgrade pip
pip install buildozer cython
pip install -r requirements_android.txt
```

#### 3. Android SDK のセットアップ

1. **Android Studio** をインストール
2. **SDK Manager** で以下をインストール:
   - Android SDK Platform 30
   - Android SDK Build-Tools 30.0.3
   - Android NDK 19b
3. 環境変数を設定:
   ```bash
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
   ```

## 🚀 APKビルド

### デバッグAPKのビルド

```bash
buildozer android debug
```

初回ビルドは30分〜1時間程度かかります。

### リリースAPKのビルド

1. **キーストアを作成:**
```bash
keytool -genkey -v -keystore my-release-key.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

2. **buildozer.spec を編集:**
```ini
[app]
android.release_artifact = apk

[buildozer]
android.keystore = my-release-key.keystore
android.keystore_key = my-key-alias
```

3. **リリースビルド実行:**
```bash
buildozer android release
```

## 📱 APKのインストール

### 開発者向け（ADB使用）

```bash
adb install bin/ocrapp-1.0-debug.apk
```

### 一般ユーザー向け

1. APKファイルをAndroid端末にコピー
2. 「設定」→「セキュリティ」→「提供元不明のアプリ」を有効化
3. APKファイルをタップしてインストール

## 🔧 カスタマイズ

### アプリ名・パッケージ名の変更

`buildozer.spec` を編集:
```ini
[app]
title = あなたのアプリ名
package.name = yourappname
package.domain = com.yourcompany.yourappname
```

### アイコンの設定

1. 512x512のPNG画像を用意
2. `icon.png` として保存
3. `buildozer.spec` で設定:
```ini
[app]
icon.filename = %(source.dir)s/icon.png
```

### 権限の調整

`buildozer.spec` で必要な権限を設定:
```ini
[app]
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
```

## 📊 ファイル構成

```
画像読み取り/
├── android_ocr_app.py          # メインアプリ
├── buildozer.spec              # ビルド設定
├── requirements_android.txt    # 依存関係
├── setup_android_build.py      # 自動セットアップ
├── android_build_guide.md      # このガイド
└── bin/                        # ビルド済みAPK
    └── ocrapp-1.0-debug.apk
```

## 🐛 トラブルシューティング

### よくある問題

#### 1. ビルドエラー: "SDK not found"
```bash
export ANDROID_HOME=/path/to/android/sdk
export ANDROID_NDK_HOME=/path/to/android/ndk
```

#### 2. メモリ不足エラー
```bash
export GRADLE_OPTS="-Xmx4g -XX:MaxPermSize=512m"
```

#### 3. NDKエラー
```ini
[app]
android.ndk = 19b  # 固定バージョンを指定
```

#### 4. 権限エラー（Android 6.0+）
アプリ内で動的権限要求を実装:
```python
from android.permissions import request_permissions, Permission
request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
```

### ログ確認

```bash
# ビルドログ
buildozer android debug -v

# アプリログ
adb logcat | grep python
```

## 🎯 最適化のヒント

### パフォーマンス向上

1. **画像サイズの制限**: 大きな画像は処理前にリサイズ
2. **メモリ管理**: 使用後は画像オブジェクトを削除
3. **バックグラウンド処理**: OCR処理は別スレッドで実行

### APKサイズ削減

1. **不要な依存関係を削除**
2. **画像圧縮**: リソース画像を最適化
3. **ProGuard使用**: コード難読化・最適化

## 🚀 配布・公開

### Google Play Store

1. **Google Play Console** アカウント作成
2. **AAB形式**でビルド:
```ini
[app]
android.release_artifact = aab
```
3. アプリ情報・スクリーンショットを準備
4. Google Playに公開申請

### 直接配布

1. **APKファイル**を配布
2. インストール手順を提供
3. **署名付きAPK**を使用

## 📞 サポート

問題が発生した場合:
1. このガイドのトラブルシューティングを確認
2. Buildozer公式ドキュメントを参照
3. ログファイルを確認して原因を特定

---

**最終更新**: 2024年12月
**対象バージョン**: Kivy 2.1.0, Buildozer 1.4.0