# controllers/joystick_control.py
import logging
import os
import sys
import pygame
import time
from gpiozero import Motor  # gpiozeroを使用してモーターを制御

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Buzzer:
    def __init__(self, sound_file='/home/ogawamasaki/School-Internship-3th-Car/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav', volume=0.7):
        # Prevent running as sudo
        if os.geteuid() == 0: 
            logging.error("Running as sudo is not allowed. Please run without sudo.")
            sys.exit(1)

        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            logging.info("pygame.mixer initialized successfully.")
        except pygame.error as e:
            logging.error(f"Error initializing pygame.mixer: {e}")
            sys.exit(1)

        # Check if sound file exists
        if not os.path.exists(sound_file):
            logging.error(f"Sound file not found: {sound_file}")
            sys.exit(1)
        else:
            logging.info(f"Sound file found: {sound_file}")

        # Load sound file
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

def joystick_control():
    """
    ジョイスティックを使用してCarを操作します。
    """
    try:
        # Initialize pygame
        pygame.init()
        pygame.joystick.init()
        logging.info("pygame initialized successfully.")

        # Check for joystick
        if pygame.joystick.get_count() == 0:
            logging.error("No joystick detected. Please connect a joystick and try again.")
            sys.exit(1)

        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        logging.info(f"Joystick '{joystick.get_name()}' initialized.")

        # Initialize buzzer
        buzzer = Buzzer()

        # Initialize motors (GPIOピンは適宜変更してください)
        left_motor = Motor(forward=17, backward=18)
        right_motor = Motor(forward=22, backward=23)
        logging.info("Motors initialized successfully.")

        # Main loop for joystick control
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    logging.info(f"Joystick button {button} pressed.")
                    # 例: ボタンが押されたときにブザーを鳴らす
                    buzzer.run('1')
                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    logging.info(f"Joystick button {button} released.")
                    # 例: ボタンが離されたときにブザーを停止する
                    buzzer.run('0')

            # 読み取った軸の値を取得
            axis_0 = joystick.get_axis(0)  # 左/右
            axis_1 = joystick.get_axis(1)  # 上/下
            logging.debug(f"Axis 0: {axis_0}, Axis 1: {axis_1}")

            # 軸の値に基づいてモーターを制御
            # 前後の移動
            if axis_1 < -0.1:
                # 前進
                left_motor.forward()
                right_motor.forward()
                logging.info("Car moving forward.")
            elif axis_1 > 0.1:
                # 後退
                left_motor.backward()
                right_motor.backward()
                logging.info("Car moving backward.")
            else:
                # 停止
                left_motor.stop()
                right_motor.stop()
                logging.info("Car stopped.")

            # 左右の回転
            if axis_0 < -0.1:
                # 左旋回
                left_motor.backward()
                right_motor.forward()
                logging.info("Car turning left.")
            elif axis_0 > 0.1:
                # 右旋回
                left_motor.forward()
                right_motor.backward()
                logging.info("Car turning right.")
            else:
                # 直進または停止（すでに前後移動で制御）
                pass

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("\nExiting joystick control gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in joystick_control: {e}")
    finally:
        # 停止処理
        left_motor.stop()
        right_motor.stop()
        pygame.quit()
        logging.info("Motors stopped and pygame has been quit.")

if __name__ == "__main__":
    # Bluetoothスピーカー接続の指示
    logging.info("First, connect the Raspberry Pi to the Bluetooth speaker.")
    logging.info("Hold down the Bluetooth speaker button until you hear a sound to indicate it's ready to connect.")

    # sudoでの実行に関する警告
    logging.info("Note: Do not run the program with sudo. Running as sudo can cause device configuration issues and errors.")
    logging.info("If the sound does not adjust or mute correctly, right-click the volume button on the top right of the Raspberry Pi 5 desktop screen and select 'Device Profile'.")

    joystick_control()
