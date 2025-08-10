import cv2

# カメラを起動
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("エラー: カメラを開けません。")
else:
    print("カメラを起動しました。'q'キーで終了します。")
    while True:
        # フレームを1枚読む
        ret, frame = cap.read()

        # フレームが読めなかった場合は終了
        if not ret:
            print("エラー: フレームをキャプチャできません。")
            break

        # ウィンドウにフレームを表示
        cv2.imshow('Camera Test', frame)

        # 'q'キーが押されたらループを抜ける
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 後処理
cap.release()
cv2.destroyAllWindows()
