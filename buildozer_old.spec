[app]

# (str) アプリケーション名
title = OCR Text Recognition

# (str) パッケージ名
package.name = ocrapp

# (str) パッケージドメイン (Google Play用)
package.domain = com.example.ocrapp

# (str) ソースディレクトリ
source.dir = .

# (list) ソースに含めるファイルパターン
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

# (str) メインのPythonファイル
source.main = android_ocr_app.py

# (str) アプリケーションバージョン
version = 1.0

# (str) アプリケーションバージョンコード
version.code = 1

# (list) アプリケーション要件
requirements = python3,kivy,pillow,opencv,numpy,plyer,android

# (str) アプリケーションアイコン
#icon.filename = %(source.dir)s/data/icon.png

# (str) サポートされる方向 (landscape, portrait, all)
orientation = portrait

# (bool) サービスとして動作するか
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# (str) 最小Android API
android.minapi = 21

# (str) ターゲットAndroid API  
android.api = 30

# (str) Android SDK バージョン
android.sdk = 30

# (str) Android NDK バージョン
android.ndk = 19b

# (list) Android権限
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO,INTERNET

# (str) プレスプラッシュ背景色
#android.presplash_color = #FFFFFF

# (str) アプリアイコンの適応アイコン背景色
#android.adaptive_icon_background_color = #FFFFFF

# (str) アプリアイコンの適応アイコン前景パス
#android.adaptive_icon_foreground = %(source.dir)s/data/icon_fg.png

# (bool) リリースビルドでアプリを署名するか
android.release_artifact = aab

# (str) リリース用キーストアファイル
#android.keystore = ~/.keystore

# (str) キーストアのキー名
#android.keystore_key = key_name

[buildozer]

# (int) ログレベル (0 = エラーのみ, 1 = 情報, 2 = デバッグ (すべてのコマンドを表示))
log_level = 2

# (str) ビルドディレクトリのパス
build_dir = ./.buildozer

# (str) binディレクトリのパス  
bin_dir = ./bin