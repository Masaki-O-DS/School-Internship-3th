# run.py
import threading
import sys
import logging
import time
from controllers.combined_control import combined_control
from controllers.joystick_control import joystick_control

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    # カメラおよびジョイスティック制御スレッドの作成
    control_thread = threading.Thread(target=combined_control, name='CombinedControlThread')
    joystick_thread = threading.Thread(target=joystick_control, name='JoystickControlThread')

    # スレッドの開始
    control_thread.start()
    logging.info("Combined control thread started.")
    
    joystick_thread.start()
    logging.info("Joystick control thread started.")

    # メインスレッドを維持
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nExiting program gracefully.")
    finally:
        # スレッドの終了を待機
        control_thread.join()
        joystick_thread.join()
        logging.info("All threads have finished. Terminating program.")
        sys.exit()

if __name__ == '__main__':
    main()
