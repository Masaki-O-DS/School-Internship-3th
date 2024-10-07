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

# ??????DEBUG???????
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

class Buzzer:
    def __init__(self, sound_file='/path/to/your/sound.wav', volume=0.7):
        # sudo???????
        if os.geteuid() == 0:
            logging.error("Running as sudo is not allowed. Please run without sudo.")
            sys.exit(1)

        # pygame mixer????
        try:
            pygame.mixer.init()
            logging.info("pygame.mixer initialized successfully.")
        except pygame.error as e:
            logging.error(f"Error initializing pygame.mixer: {e}")
            sys.exit(1)

        # ?????????????
        if not os.path.exists(sound_file):
            logging.error(f"Sound file not found: {sound_file}")
            sys.exit(1)
        else:
            logging.info(f"Sound file found: {sound_file}")

        # ?????????????
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
        self.integral_limit = integral_limit  # ??????

    def compute(self, measurement, dt):
        error = self.setpoint - measurement

        if error != 0:
            self.integral += error * dt
            # ????????
            self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)
        else:
            # ????????????????
            self.integral = 0.0

        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error

        logging.debug(f"PID Compute -> Error: {error}, Inte
