# run.py

import threading
import time
import sys
from controllers.joystick_control import joystick_control
from controllers.camera_control import camera_control

def main():
    # ジョイスティック制御スレッドの作成
    joystick_thread = threading.Thread(target=joystick_control, name='JoystickControlThread')

    # カメラ制御スレッドの作成
    camera_thread = threading.Thread(target=camera_control, name='CameraControlThread')

    # スレッドをデーモンとして開始（メインスレッドが終了すると同時に終了）
    joystick_thread.daemon = True
    camera_thread.daemon = True

    joystick_thread.start()
    camera_thread.start()

    print("ジョイスティック制御とカメラ制御を開始しました。")

    try:
        # メインスレッドはスレッドが終了するのを待機
        while True:
            if not joystick_thread.is_alive() or not camera_thread.is_alive():
                print("いずれかのスレッドが停止しました。プログラムを終了します。")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
    finally:
        print("すべてのスレッドを終了しました。")
        sys.exit()

if __name__ == '__main__':
    main()
