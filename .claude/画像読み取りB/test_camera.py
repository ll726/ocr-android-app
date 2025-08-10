import cv2

for i in range(3):
    print(f"Testing camera {i}...")
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    print(f"Camera {i}: {'OK' if ret else 'Failed'}")
    cap.release()