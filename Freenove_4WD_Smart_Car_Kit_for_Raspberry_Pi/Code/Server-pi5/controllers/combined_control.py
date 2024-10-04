# controllers/combined_control.py
import cv2
from cv2 import aruco
from picamera2 import Picamera2
import time
import logging
import threading
import os
import sys

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def combined_control():
    """
    カメラアクセス、ARマーカー検出、およびブザー制御を統合的に管理します。
    """
    picam2 = None
    try:
        # Picamera2の初期化
        picam2 = Picamera2()
        resolution = (640, 480)
        preview_config = picam2.create_preview_configuration(
            main={"format": 'RGB888', "size": resolution}
        )
        picam2.configure(preview_config)
        picam2.start()
        logging.info("Camera started successfully.")

        # ARUCOの初期化
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        parameters = aruco.DetectorParameters_create()
        parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

        # FPS計算の初期化
        frame_count = 0
        start_time = time.time()
        fps = 0

        def update_fps():
            nonlocal frame_count, start_time, fps
            while True:
                time.sleep(0.5)
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    fps = frame_count / elapsed_time
                    logging.info(f"FPS: {fps:.2f}")
                    frame_count = 0
                    start_time = time.time()

        # FPS更新スレッドの開始
        fps_thread = threading.Thread(target=update_fps, daemon=True)
        fps_thread.start()

        # imgフォルダのパスを設定
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(os.path.dirname(script_dir), 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            logging.info(f"Image directory created at {img_dir}")

        # Initialize buzzer control via GPIO (別の方法でブザーを制御)
        # 例としてGPIOピンを使用してブザーを制御する場合
        from gpiozero import Buzzer as GPIOBuzzer
        buzzer_gpio = GPIOBuzzer(27)  # ブザーが接続されているGPIOピンを指定

        while True:
            # カメラからのフレームキャプチャ
            frame = picam2.capture_array()

            # フレームの検証
            if frame is None or frame.size == 0:
                logging.warning("Empty frame captured. Skipping frame processing.")
                continue

            # グレースケール変換
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # ARUCOマーカーの検出
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            # 検出結果の描画
            if ids is not None:
                frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"aruco_detected_{timestamp}.png"
                filepath = os.path.join(img_dir, filename)
                cv2.imwrite(filepath, frame_markers)
                logging.info(f"AR marker detected. Image saved as {filepath}")
                # ブザーの鳴動 (GPIOを使用)
                buzzer_gpio.on()
            else:
                frame_markers = frame.copy()
                buzzer_gpio.off()  # ブザーをオフにする

            # フレームの表示
            cv2.imshow("AR Marker Detection", frame_markers)

            # FPSカウントの更新
            frame_count += 1

            # 'q'キーでループを抜ける
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Stopping camera feed.")
                break

    except KeyboardInterrupt:
        logging.info("\nExiting combined control gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in combined_control: {e}")
    finally:
        # カメラの停止とウィンドウの閉鎖
        if picam2 is not None:
            try:
                picam2.stop()
                logging.info("Camera stopped successfully.")
            except Exception as e:
                logging.error(f"Error stopping camera: {e}")
        # ブザーの停止
        try:
            buzzer_gpio.off()
            logging.info("Buzzer turned off.")
        except:
            pass
        cv2.destroyAllWindows()
        logging.info("Camera and OpenCV windows have been closed.")

if __name__ == "__main__":
    # Bluetoothスピーカー接続の指示
    logging.info("First, connect the Raspberry Pi to the Bluetooth speaker.")
    logging.info("Hold down the Bluetooth speaker button until you hear a sound to indicate it's ready to connect.")

    # sudoでの実行に関する警告
    logging.info("Note: Do not run the program with sudo. Running as sudo can cause device configuration issues and errors.")
    logging.info("If the sound does not adjust or mute correctly, right-click the volume button on the top right of the Raspberry Pi 5 desktop screen and select 'Device Profile'.")

    combined_control()
