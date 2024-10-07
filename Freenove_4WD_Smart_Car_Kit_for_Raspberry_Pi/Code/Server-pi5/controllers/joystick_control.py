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
        # sudoで実行されていることを確認（GPIO操作には必要）
        if os.geteuid() != 0:
            logging.error("This program requires root privileges. Please run with sudo.")
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
    def __init__(self, kp, ki, kd, setpoint=0, integral_limit=10.0, epsilon=1e-5):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.integral = 0.0
        self.previous_error = 0.0
        self.integral_limit = integral_limit  # 積分項の上限
        self.epsilon = epsilon  # 誤差の閾値

    def compute(self, measurement, dt):
        error = self.setpoint - measurement

        if abs(error) > self.epsilon:
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
    TURN_SPEED_FACTOR = 0.6  # 旋回速度を60%に設定
    SERVO_NECK_UP = 160
    SERVO_NECK_DOWN = 120
    SERVO_NECK_NEUTRAL = 90

    # PIDコントローラーの初期化
    pid_y = PIDController(kp=1.0, ki=0.1, kd=0.05, integral_limit=10.0, epsilon=1e-5)

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
                        button = event.butto
