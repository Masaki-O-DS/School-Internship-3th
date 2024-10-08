# controllers/joystick_control.py
import time
import sys
import pygame
from Motor import Motor
from servo import Servo
import logging
import os
import queue
import threading  # 追加

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')  # ログレベルをINFOに設定

class Buzzer:
    def __init__(self, sound_file='/home/ogawamasaki/School-Internship-3th-Car/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav', volume=0.7):
        # sudoでの実行を防止
        if os.geteuid() == 0:
            logging.error("Running as sudo is not allowed. Please run without sudo.")
            sys.exit(1)

        # pygame mixerの初期化
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

        # サウンドファイルの読み込み
        try:
            self.sound = pygame.mixer.Sound(sound_file)
            self.sound.set_volume(volume)
            logging.info("Sound file loaded successfully.")
        except pygame.error as e:
            logging.error(f"Error loading sound file: {e}")
            sys.exit(1)

    def play(self):
        logging.info("Buzzer ON: Playing sound.")
        self.sound.play()

    def stop(self):
        logging.info("Buzzer OFF: Stopping sound.")
        self.sound.stop()

# 定数の定義
BUTTON_R1 = 5  # R1ボタンのインデックス（必要に応じて調整）

# 旋回パラメータ（調整可能）
ROTATE_PARAMS = {
    'right': {
        'duration': 0.5,    # 90度回転に必要な時間（秒）（実際のハードウェアに合わせて調整）
        'speed': 4000       # 旋回時の速度（PWM値）（デフォルト: 4000）
    },
    'left': {
        'duration': 5.0,    # 左旋回用のパラメータ
        'speed': 4000
    }
}

# 旋回中かどうかを示すイベント
rotation_event = threading.Event()

def perform_rotation(motor, direction='right', duration=5.0, speed=4000):
    """
    指定された方向に指定された速度と時間で旋回を実行します。

    :param motor: Motorオブジェクト
    :param direction: 'left' または 'right'
    :param duration: 旋回にかかる時間（秒）
    :param speed: 旋回時の速度（PWM値）
    """
    try:
        rotation_event.set()  # 旋回開始
        logging.info(f"90度回転開始: {direction}方向、速度: {speed}, 時間: {duration}秒")
        motor.Rotate(direction, speed=speed)
        time.sleep(duration)
        motor.stop()
        logging.info("90度回転完了")
    except Exception as e:
        logging.error(f"旋回中にエラーが発生しました: {e}")
        motor.stop()
    finally:
        rotation_event.clear()  # 旋回終了

def joystick_control(audio_queue):
    """
    ジョイスティックで車とサーボを制御し、Bluetoothスピーカーで音声を再生します。
    """
    SERVO_NECK_CHANNEL = '1'  # サーボチャンネルを関数の先頭で初期化
    motor = None
    servo = None
    buzzer = None

    try:
        # ハードウェアコンポーネントの初期化
        motor = Motor()
        servo = Servo()

        # Pygameの初期化
        pygame.init()

        # ジョイスティックの初期化
        pygame.joystick.init()

        # 接続されているジョイスティックの数を取得
        joystick_count = pygame.joystick.get_count()
        logging.info(f"Number of joysticks connected: {joystick_count}")

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            logging.info(f"Joystick name: {joystick.get_name()}")
            logging.info(f"Number of axes: {joystick.get_numaxes()}")
            logging.info(f"Number of buttons: {joystick.get_numbuttons()}")
            logging.info(f"Number of hats: {joystick.get_numhats()}")

            # ジョイスティックのボタン一覧をログに出力（デバッグ用）
            for i in range(joystick.get_numbuttons()):
                logging.info(f"Button {i}: Initial state: {joystick.get_button(i)}")
        else:
            logging.error("No joysticks connected. Exiting program.")
            return  # ジョイスティックが接続されていない場合は終了

        # ブザーの初期化
        buzzer = Buzzer()

        # デッドゾーンの設定
        DEAD_ZONE_MOVEMENT = 0.2
        DEAD_ZONE_TURN = 0.2

        # 最大PWM値
        MAX_PWM = 4095

        # 旋回速度スケーリングファクター
        TURN_SPEED_FACTOR = 0.3  # 旋回速度を30%に設定（以前より低速に変更）

        # サーボ角度の定義（0°から180°）
        SERVO_NECK_UP = 160    # サーボを上に移動
        SERVO_NECK_DOWN = 120  # サーボを下に移動
        SERVO_NECK_NEUTRAL = 90  # サーボの中立位置

        # サーボを中立位置に設定
        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
        logging.info("Servo0 set to neutral position.")

        # クロックの初期化（FPS制御用）
        clock = pygame.time.Clock()

        while True:
            try:
                # イベントの処理
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return  # ループを抜ける

                    elif event.type == pygame.JOYBUTTONDOWN:
                        button = event.button
                        logging.info(f"Button {button} pressed.")

                        # サーボ制御
                        if button == 6:  # L2 Trigger
                            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_DOWN)
                            logging.info(f"Servo0 moved down to {SERVO_NECK_DOWN} degrees.")
                        elif button == 7:  # R2 Trigger
                            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_UP)
                            logging.info(f"Servo0 moved up to {SERVO_NECK_UP} degrees.")

                        # 特定のボタン押下でブザーを再生
                        if button == 0:
                            buzzer.play()

                        # R1ボタン押下で90度回転（旋回中でない場合）
                        if button == BUTTON_R1 and not rotation_event.is_set():
                            logging.info("R1ボタンが押されました。90度回転を開始します。")
                            # パラメータを変更したい場合は以下の値を調整してください
                            rotation_direction = 'right'  # 'left' または 'right'
                            rotation_duration = ROTATE_PARAMS[rotation_direction]['duration']
                            rotation_speed = ROTATE_PARAMS[rotation_direction]['speed']
                            threading.Thread(
                                target=perform_rotation,
                                args=(motor, rotation_direction, rotation_duration, rotation_speed),
                                daemon=True
                            ).start()
                        elif button == BUTTON_R1 and rotation_event.is_set():
                            logging.info("現在旋回中です。R1ボタンの押下を無視します。")

                    elif event.type == pygame.JOYBUTTONUP:
                        button = event.button
                        # サーボを中立位置に戻す
                        if button in [6, 7]:
                            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
                            logging.info("Servo0 reset to neutral position.")

                        # ブザーの停止
                        if button == 0:
                            buzzer.stop()

                # 旋回中の場合、ジョイスティック入力を無視
                if rotation_event.is_set():
                    logging.info("旋回中のため、ジョイスティック入力を無視します。")
                    clock.tick(60)
                    continue  # ループの先頭に戻る

                # ジョイスティックの軸入力を取得
                left_vertical = joystick.get_axis(1)      # 左スティックY軸（前後）
                left_horizontal = joystick.get_axis(0)    # 左スティックX軸（左右）
                right_horizontal = joystick.get_axis(3)   # 右スティックX軸（旋回）

                # 生の軸値をログに表示（デバッグ用）
                logging.debug(f"Raw axes: {[joystick.get_axis(i) for i in range(joystick.get_numaxes())]}")

                # デッドゾーンの適用
                if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                    left_vertical = 0
                if abs(left_horizontal) < DEAD_ZONE_MOVEMENT:
                    left_horizontal = 0
                if abs(right_horizontal) < DEAD_ZONE_TURN:
                    right_horizontal = 0

                # 移動方向の計算
                y = -left_vertical      # 前後の動き（反転）
                x = left_horizontal     # 左右の動き
                turn = right_horizontal * (TURN_SPEED_FACTOR if (x == 0 and y == 0) else 0.7)  # 左スティックと連動時は旋回速度を調整

                # PWM値への変換（-4095から4095）
                duty_y = int(y * MAX_PWM)
                duty_x = int(x * MAX_PWM)
                duty_turn = int(turn * MAX_PWM)

                # メカナムホイール用のPWM値の計算（全方向移動をサポート）
                # 左右移動と旋回が連動するように計算
                duty_front_left = duty_y + duty_x + duty_turn
                duty_front_right = duty_y - duty_x - duty_turn
                duty_back_left = duty_y - duty_x + duty_turn
                duty_back_right = duty_y + duty_x - duty_turn

                # PWM値を制限（-4095～4095）
                duty_front_left = max(min(duty_front_left, MAX_PWM), -MAX_PWM)
                duty_front_right = max(min(duty_front_right, MAX_PWM), -MAX_PWM)
                duty_back_left = max(min(duty_back_left, MAX_PWM), -MAX_PWM)
                duty_back_right = max(min(duty_back_right, MAX_PWM), -MAX_PWM)

                # PWM値をログに表示（デバッグ用）
                logging.debug(f"PWM values - FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

                # 旋回中かどうかを判定
                is_turning = (turn != 0)

                # モーターにPWM値を送信
                motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right, turning=is_turning)

                # デバッグログの強化（スケーリング後のPWM値を表示）
                logging.debug(f"Scaled PWM values - FL: {int(duty_front_left * motor.left_motor_scaling * (0.7 if is_turning else 0.8))}, "
                              f"FR: {duty_front_right}, "
                              f"BL: {int(duty_back_left * motor.left_motor_scaling * (0.7 if is_turning else 0.8))}, "
                              f"BR: {duty_back_right}")

                # キューからの音声再生指示を処理
                try:
                    while not audio_queue.empty():
                        command = audio_queue.get_nowait()
                        if command == "PLAY_AR_SOUND":
                            buzzer.play()
                        elif command == "STOP_AR_SOUND":
                            buzzer.stop()
                        elif command is None:
                            logging.info("Joystick control thread received exit signal.")
                            raise KeyboardInterrupt
                except queue.Empty:
                    pass

                # FPSを60に制限
                clock.tick(60)

            except IOError as e:
                logging.error(f"I/O error occurred: {e}. Attempting to continue.")
                if motor:
                    motor.setMotorModel(0, 0, 0, 0)
                if servo:
                    servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
                time.sleep(1)  # 再試行前に待機
            except Exception as e:
                logging.error(f"Unexpected error: {e}. Exiting joystick control thread.")
                raise

    except KeyboardInterrupt:
        logging.info("\nExiting joystick control thread.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        try:
            if motor:
                # モーターを停止
                motor.setMotorModel(0, 0, 0, 0)
            if servo:
                # サーボを中立位置に戻す
                servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
            logging.info("Motors stopped and Servo0 reset to neutral position.")
        except Exception as e:
            logging.error(f"Error while stopping motors or resetting servo: {e}")
        pygame.quit()
