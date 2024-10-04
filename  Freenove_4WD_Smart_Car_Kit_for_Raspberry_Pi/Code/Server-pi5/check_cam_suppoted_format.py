from picamera2 import Picamera2

# カメラを初期化
picam2 = Picamera2()

# サポートされているフォーマットを取得
supported_formats = picam2.sensor_modes

# フォーマットを表示
for mode in supported_formats:
    print(f"Format: {mode['format']}")
    print(f"Size: {mode['size']}")
    print(f"FPS: {mode['fps']}")
    print("---")

# 利用可能な設定を表示
print("Available configurations:")
print(picam2.sensor_modes)