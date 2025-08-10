[app]

# (str) Application title
title = OCR Text Recognition

# (str) Package name
package.name = ocrapp

# (str) Package domain (Google Play)
package.domain = com.example.ocrapp

# (str) Source directory
source.dir = .

# (list) Source include extensions
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

# (str) Main Python file
source.main = android_ocr_app.py

# (str) Application version
version = 1.0

# (str) Application version code
version.code = 1

# (list) Application requirements
requirements = python3,kivy,pillow,opencv,numpy,plyer,android

# (str) Application icon
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, portrait, all)
orientation = portrait

# (str) Minimum Android API
android.minapi = 21

# (str) Target Android API
android.api = 30

# (str) Android NDK version
android.ndk = 23b

# (str) Android SDK directory
#android.sdk_path = 

# (str) Android NDK directory
#android.ndk_path = 

# (list) Android permissions
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (bool) Enable Android auto backup feature
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (str) Build directory path
build_dir = ./.buildozer

# (str) Bin directory path  
bin_dir = ./bin