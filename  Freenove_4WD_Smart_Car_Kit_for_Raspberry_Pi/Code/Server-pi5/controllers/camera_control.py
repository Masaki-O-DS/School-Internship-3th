# controllers/camera_control.py

import cv2
from cv2 import aruco
from picamera2 import Picamera2, Preview
import time

def camera_control():
    """
    カメラからの映像を取得し、ARマーカーを検出して表示します。
    """
    try:
        # Picamera2の初期化
        picam2 = Picamera2()
        preview_config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)})
        picam2.configure(preview_config)
        picam2.start()
        print("カメラを開始しました。")

        # ARマーカーの設定
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)  # 4x4bitのARマーカー
        parameters = aruco.DetectorParameters_create()

        while True:
            # カメラ画像を取得
            frame = picam2.capture_array()

            # 画像を前処理:RGBからグレースケールに変換
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # ARマーカー検知
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            # 検知箇所を画像にマーキング
            frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
            cv2.imshow("ARマーカー検出結果", cv2.cvtColor(frame_markers, cv2.COLOR_BGR2RGB))

            # キー入力がある場合は終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("カメラを停止します。")
                break

            # 少し待機
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nカメラプログラムを終了します。")
    except Exception as e:
        print(f"カメラプログラム中にエラーが発生しました: {e}")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
