# WSL セットアップガイド
## Android APKビルド環境構築

### 📋 WSL（Windows Subsystem for Linux）とは？
- Windows上でLinuxを動作させる機能
- Android APKビルドに必要なLinux環境を提供
- コマンドプロンプトからLinuxコマンドを実行可能

## 🚀 WSL インストール手順

### Step 1: WSL を有効化

#### **方法1: コマンドプロンプト（管理者権限）で実行**
```cmd
wsl --install
```

#### **方法2: 手動で有効化**
1. **Windows機能の有効化または無効化** を開く
2. 以下にチェックを入れる：
   - ✅ Linux 用 Windows サブシステム
   - ✅ 仮想マシン プラットフォーム
3. 再起動

### Step 2: Ubuntu をインストール

#### **Microsoft Store から:**
1. Microsoft Store を開く
2. "Ubuntu 22.04.3 LTS" を検索
3. インストールをクリック

#### **コマンドから:**
```cmd
wsl --install -d Ubuntu-22.04
```

### Step 3: Ubuntu 初期設定

1. **Ubuntu を起動**（スタートメニューから）
2. **ユーザー名とパスワードを設定**
   ```
   Enter new UNIX username: your_username
   Enter new UNIX password: ********
   ```

### Step 4: システム更新

```bash
sudo apt update
sudo apt upgrade -y
```

## 🔧 Android ビルド環境構築

### Step 1: 必要なパッケージをインストール

```bash
# 基本開発ツール
sudo apt install -y build-essential git python3 python3-pip

# Android開発用
sudo apt install -y openjdk-8-jdk
sudo apt install -y wget curl unzip

# Kivy/Buildozer依存関係
sudo apt install -y python3-dev ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev \
    libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0 \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

### Step 2: Windowsファイルにアクセス

```bash
# Windowsファイルはここにある
cd /mnt/c/Users/m/Documents/画像読み取り/

# ファイル一覧確認
ls -la
```

### Step 3: Pythonパッケージインストール

```bash
# pip更新
pip3 install --upgrade pip

# Buildozer関連
pip3 install buildozer cython

# アプリ依存関係
pip3 install kivy pillow opencv-python numpy plyer
```

### Step 4: Android SDK セットアップ

#### **Android Studio をインストール（Windows側）**
1. https://developer.android.com/studio からダウンロード
2. インストール後、SDK Manager で以下をインストール：
   - Android SDK Platform 30
   - Android SDK Build-Tools 30.0.3
   - Android NDK 19b

#### **環境変数設定（WSL側）**
```bash
# ~/.bashrc に追加
echo 'export ANDROID_HOME="/mnt/c/Users/$USER/AppData/Local/Android/Sdk"' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools' >> ~/.bashrc

# 設定を反映
source ~/.bashrc
```

## 📱 APK ビルド実行

### Step 1: プロジェクトディレクトリに移動

```bash
cd /mnt/c/Users/m/Documents/画像読み取り/
```

### Step 2: 自動セットアップ実行

```bash
python3 setup_android_build.py
```

### Step 3: APK ビルド

```bash
# デバッグAPKビルド（初回は30分～1時間）
buildozer android debug
```

### Step 4: APK確認

```bash
# 生成されたAPKを確認
ls -la bin/
# ocrapp-1.0-debug.apk が作成されている
```

## 🔍 トラブルシューティング

### 問題: WSLインストールエラー
**解決策:**
```cmd
# 管理者権限でコマンドプロンプトを開き
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### 問題: buildozerエラー
**解決策:**
```bash
# キャッシュクリア
buildozer android clean

# 詳細ログでビルド
buildozer android debug -v
```

### 問題: 権限エラー
**解決策:**
```bash
# ファイル権限修正
sudo chmod +x setup_android_build.py
sudo chown -R $USER:$USER .buildozer/
```

## 🎯 コマンド早見表

### WSL操作
```bash
# WSL起動
wsl

# WSL終了
exit

# Windows→Linux パス変換例
# C:\Users\m\Documents → /mnt/c/Users/m/Documents
```

### Android開発
```bash
# プロジェクト移動
cd /mnt/c/Users/m/Documents/画像読み取り/

# デバッグAPKビルド
buildozer android debug

# リリースAPKビルド
buildozer android release

# クリーンビルド
buildozer android clean
```

### ファイル転送
```bash
# Windows側にコピー
cp bin/ocrapp-1.0-debug.apk /mnt/c/Users/m/Desktop/

# Android端末にインストール（adb使用）
adb install bin/ocrapp-1.0-debug.apk
```

## ⚡ 簡単セットアップスクリプト

自動でWSL環境を構築するスクリプトも作成できます：

```bash
#!/bin/bash
# wsl_quick_setup.sh

echo "Android APK Build Environment Setup for WSL"
echo "==========================================="

# システム更新
sudo apt update && sudo apt upgrade -y

# 必要パッケージ一括インストール
sudo apt install -y build-essential git python3 python3-pip openjdk-8-jdk \
    wget curl unzip python3-dev ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev \
    libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0 \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good

# Python環境構築
pip3 install --upgrade pip
pip3 install buildozer cython kivy pillow opencv-python numpy plyer

echo "Setup completed!"
echo "Next steps:"
echo "1. Install Android Studio on Windows"
echo "2. Set ANDROID_HOME environment variable"
echo "3. Run: cd /mnt/c/Users/m/Documents/画像読み取り/"
echo "4. Run: buildozer android debug"
```

---

**最終更新**: 2024年12月  
**対象**: Windows 10/11 + WSL2 + Ubuntu 22.04