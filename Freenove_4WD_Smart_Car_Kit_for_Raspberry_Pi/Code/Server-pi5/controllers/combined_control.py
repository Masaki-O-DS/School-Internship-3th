# controllers/combined_control.py
import cv2
from cv2 import aruco
from picamera2 import Picamera2
import time
import logging
import threading
import os
import sys
import pygame

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Buzzer:
    def __init__(self, sound_file='/home/ogawamasaki/School-Internship-3th-Car/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav', volume=0.7):
        # sudoでの実行を防止
        if os.geteuid() == 0:
            logging.error("Running as sudo is not allowed. Please run without sudo.")
            sys.exit(1)

        # pygameミキサーの初期化
        try:
            pygame.mixer.init()
            logging.info("pygame.mixer initialized successfully.")
        except pygame.error as e:
            logging.error(f"Error initializing pygame.mixer: {e}")
            sys.exit(1)

        # サウンドファイルの存在確認
        if not os.path.exists(sound_file):
            logging.error(f"Sound file not found: {sound_file}")
            sys.exit(1)
        else:
            logging.info(f"Sound file found: {sound_file}")

        # サウンドファイルのロード
        try:
            self.sound = pygame.mixer.Sound(sound_file)
            self.sound.set_volume(volume)
            logging.info("Sound file loaded successfully.")
        except pygame.error as e:
            logging.error(f"Error loading sound file: {e}")
            sys.exit(1)

    def run(self, command):
        if command != "0":
            logging.info("Buzzer ON: Playing sound.")
            self.sound.play()
        else:
            logging.info("Buzzer OFF: Stopping sound.")
            self.sound.stop()

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

        # ブザーの初期化
        buzzer = Buzzer(sound_file='/home/ogawamasaki/School-Internship-3th-Car/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav')

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
                cv2.imwrite(filename, frame_markers)
                logging.info(f"AR marker detected. Image saved as {filename}")
                # ブザーの鳴動
                buzzer.run('1')
            else:
                frame_markers = frame.copy()
                buzzer.run('0')  # ブザーをオフにする

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
