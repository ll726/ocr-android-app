
from PIL import Image, ImageDraw, ImageFont

# 画像サイズ
width = 400
height = 100

# 背景色
background_color = "white"

# テキスト
text = "こんにちは、世界！"
font_color = "black"

# Windowsに標準で入っている日本語フォントを指定
# フォントファイルが見つからない場合は、'C:\Windows\Fonts\' などで探してください
font_path = "C:\\Windows\\Fonts\\msgothic.ttc" 
try:
    font = ImageFont.truetype(font_path, 32)
except IOError:
    print(f"フォントが見つかりません: {font_path}")
    # 代替フォントとしてデフォルトフォントを試みる
    try:
        font = ImageFont.load_default()
        print("デフォルトフォントを使用します。日本語は表示されない可能性があります。")
    except Exception as e:
        print(f"デフォルトフォントの読み込みに失敗しました: {e}")
        font = None

# 画像を生成
if font:
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # テキストを描画
    draw.text((10, 10), text, font=font, fill=font_color)

    # ファイルに保存
    image.save("test_image_jp.png")
    print("テスト画像 'test_image_jp.png' を作成しました。")
else:
    print("フォントの準備ができなかったため、画像を作成できませんでした。")
