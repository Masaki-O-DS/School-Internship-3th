# controllers/joystick_control.py

import time
import sys
import pygame
from Motor import Motor
from servo import Servo
import logging
import os
import queue
import math
import threading
import RPi.GPIO as GPIO

# ログの設定（DEBUGレベルに設定）
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

class Buzzer:
    def __init__(self, sound_file='/path/to/your/sound.wav', volume=0.7):
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

class PIDController:
    def __init__(self, kp, ki, kd, setpoint=0, integral_limit=10.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.integral = 0.0
        self.previous_error = 0.0
        self.integral_limit = integral_limit  # 積分項の上限

    def compute(self, measurement, dt):
        error = self.setpoint - measurement

        if error != 0:
            self.integral += error * dt
            # 積分項をクランプ
            self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)
        else:
            # 誤差がない場合、積分項をリセット
            self.integral = 0.0

        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error

        logging.debug(f"PID Compute -> Error: {error}, Integral: {self.integral}, Derivative: {derivative}, Output: {output}")
        return output

def nonlinear_scale(value, exponent=2):
    """
    ジョイスティックの入力を非線形にスケーリングする関数
    exponentの値を調整することで応答曲線を変更可能
    """
    if value == 0:
        return 0.0
    return math.copysign(abs(value) ** exponent, value)

class Encoder:
    def __init__(self, pin_a, pin_b):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.count = 0
        self.lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self.update_count)
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self.update_count)

    def update_count(self, channel):
        with self.lock:
            a = GPIO.input(self.pin_a)
            b = GPIO.input(self.pin_b)
            if a == b:
                self.count += 1
            else:
                self.count -= 1

    def get_speed(self, dt):
        with self.lock:
            speed = self.count / dt  # エンコーダーの仕様に基づいて調整
            self.count = 0
        return speed

    def cleanup(self):
        GPIO.cleanup()

def joystick_control(audio_queue):
    SERVO_NECK_CHANNEL = '1'
    motor = None
    servo = None
    buzzer = None

    # 制御パラメータの設定
    DEAD_ZONE_MOVEMENT = 0.15  # デッドゾーンを0.15に増加
    DEAD_ZONE_TURN = 0.15
    MAX_PWM = 4095
    TURN_SPEED_FACTOR = 0.6  # 旋回速度を60%に増加
    SERVO_NECK_UP = 160
    SERVO_NECK_DOWN = 120
    SERVO_NECK_NEUTRAL = 90

    # PIDコントローラーの初期化
    pid_y = PIDController(kp=1.0, ki=0.1, kd=0.05, integral_limit=10.0)

    # エンコーダーの初期化（GPIOピン番号を適宜設定）
    encoder = Encoder(pin_a=17, pin_b=18)  # 例: GPIO17とGPIO18を使用

    try:
        motor = Motor()
        servo = Servo()

        pygame.init()
        pygame.joystick.init()

        joystick_count = pygame.joystick.get_count()
        logging.info(f"Number of joysticks connected: {joystick_count}")

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            logging.info(f"Joystick name: {joystick.get_name()}")
            logging.info(f"Number of axes: {joystick.get_numaxes()}")
            logging.info(f"Number of buttons: {joystick.get_numbuttons()}")
            logging.info(f"Number of hats: {joystick.get_numhats()}")
        else:
            logging.error("No joysticks connected. Exiting program.")
            return

        buzzer = Buzzer()

        # サーボを中立位置に設定
        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
        logging.info("Servo0 set to neutral position.")

        clock = pygame.time.Clock()
        last_time = time.time()

        while True:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                    elif event.type == pygame.JOYBUTTONDOWN:
                        button = event.button
                        logging.info(f"Button {button} pressed.")

                        if button == 6:
                            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_DOWN)
                            logging.info(f"Servo0 moved down to {SERVO_NECK_DOWN} degrees.")
                        elif button == 7:
                            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_UP)
                            logging.info(f"Servo0 moved up to {SERVO_NECK_UP} degrees.")

                        if button == 0:
                            buzzer.play()

                    elif event.type == pygame.JOYBUTTONUP:
                        button = event.button
                        if button in [6, 7]:
                            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
                            logging.info("Servo0 reset to neutral position.")

                        if button == 0:
                            buzzer.stop()

                # ジョイスティックの軸入力を取得
                left_vertical = joystick.get_axis(1)
                left_horizontal = joystick.get_axis(0)
                right_horizontal = joystick.get_axis(3)

                # デッドゾーンの適用
                if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                    left_vertical = 0.0
                if abs(left_horizontal) < DEAD_ZONE_MOVEMENT:
                    left_horizontal = 0.0
                if abs(right_horizontal) < DEAD_ZONE_TURN:
                    right_horizontal = 0.0

                # ジョイスティック入力を非線形にスケーリング
                y_input = nonlinear_scale(-left_vertical, exponent=2)      # 前後の動き（反転）
                x_input = nonlinear_scale(left_horizontal, exponent=2)     # 左右の動き
                turn_input = nonlinear_scale(right_horizontal * (TURN_SPEED_FACTOR if (x_input == 0.0 and y_input == 0.0) else 0.8), exponent=2)

                # 時間差の計算
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # エンコーダーから現在の速度を取得
                current_speed = encoder.get_speed(dt)  # 実際の速度センサーから取得

                # PIDコントローラーのセットポイント設定
                pid_y.setpoint = y_input * 1.0  # 目標速度を設定（必要に応じて調整）
                control_y = pid_y.compute(measurement=current_speed, dt=dt)

                # PWM値への変換
                duty_y = int(control_y * MAX_PWM)
                duty_x = int(x_input * MAX_PWM)
                duty_turn = int(turn_input * MAX_PWM)

                # PWM値を制限（-4095～4095）
                duty_y = max(min(duty_y, MAX_PWM), -MAX_PWM)
                duty_x = max(min(duty_x, MAX_PWM), -MAX_PWM)
                duty_turn = max(min(duty_turn, MAX_PWM), -MAX_PWM)

                # メカナムホイール用のPWM値の計算
                duty_front_left = duty_y + duty_x + duty_turn
                duty_front_right = duty_y - duty_x - duty_turn
                duty_back_left = duty_y - duty_x + duty_turn
                duty_back_right = duty_y + duty_x - duty_turn

                # PWM値を制限（-4095～4095）
                duty_front_left = max(min(duty_front_left, MAX_PWM), -MAX_PWM)
                duty_front_right = max(min(duty_front_right, MAX_PWM), -MAX_PWM)
                duty_back_left = max(min(duty_back_left, MAX_PWM), -MAX_PWM)
                duty_back_right = max(min(duty_back_right, MAX_PWM), -MAX_PWM)

                # デバッグログを追加
                logging.debug(f"Raw Joystick Inputs -> Left Vertical: {left_vertical}, Left Horizontal: {left_horizontal}, Right Horizontal: {right_horizontal}")
                logging.debug(f"Joystick Inputs -> Y: {y_input}, X: {x_input}, Turn: {turn_input}")
                logging.debug(f"PID Output -> control_y: {control_y}")
                logging.debug(f"PWM Values -> FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

                # モーターにPWM値を送信
                motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right)

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

                # 制御ループのFPSを120に設定
                clock.tick(120)

            except IOError as e:
                logging.error(f"I/O error occurred: {e}. Attempting to continue.")
                if motor:
                    motor.setMotorModel(0, 0, 0, 0)
                if servo:
                    servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
                time.sleep(1)
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
                motor.setMotorModel(0, 0, 0, 0)
            if servo:
                servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
            logging.info("Motors stopped and Servo0 reset to neutral position.")
        except Exception as e:
            logging.error(f"Error while stopping motors or resetting servo: {e}")
        # エンコーダーのクリーンアップ
        encoder.cleanup()
        pygame.quit()
