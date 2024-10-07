# run.py
import threading
import sys
import logging
import time
from controllers.joystick_control import joystick_control
from controllers.camera_control import camera_control
import queue

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')  # ログレベルをINFOに設定

def main():
    # スレッド間通信用のキューを作成
    audio_queue = queue.Queue()

    # ジョイスティック制御スレッドの作成
    joystick_thread = threading.Thread(target=joystick_control, args=(audio_queue,), name='JoystickControlThread')

    # カメラ制御スレッドの作成
    camera_thread = threading.Thread(target=camera_control, args=(audio_queue,), name='CameraControlThread')

    # スレッドの開始
    joystick_thread.start()
    logging.info("Joystick control thread started.")

    camera_thread.start()
    logging.info("Camera control thread started.")

    # メインスレッドを維持
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nExiting program gracefully.")
    finally:
        # スレッドに終了を通知（キューにNoneを送信）
        audio_queue.put(None)

        # スレッドの終了を待機
        joystick_thread.join()
        camera_thread.join()
        logging.info("All threads have finished. Terminating program.")
        sys.exit()

if __name__ == '__main__':
    main()
