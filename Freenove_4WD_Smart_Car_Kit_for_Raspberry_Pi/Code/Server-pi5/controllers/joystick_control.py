# controllers/joystick_control.py
import cv2
from cv2 import aruco
from picamera2 import Picamera2
import time
import logging
import threading
import os
import sys
import pygame

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Buzzer:
    def __init__(self, sound_file='/Users/ogawamaki/Desktop/School-Internship-3th-Car/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav', volume=0.7):
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

        # Main loop for joystick control
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    logging.info(f"Joystick button {button} pressed.")
                    # Example: Play buzzer sound on button press
                    buzzer.run('1')
                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    logging.info(f"Joystick button {button} released.")
                    # Example: Stop buzzer sound on button release
                    buzzer.run('0')

            # Example: Read axis values for movement
            axis_0 = joystick.get_axis(0)  # Left/Right
            axis_1 = joystick.get_axis(1)  # Up/Down
            logging.debug(f"Axis 0: {axis_0}, Axis 1: {axis_1}")

            # Implement car control logic based on axis values here

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("\nExiting joystick control gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in joystick_control: {e}")
    finally:
        pygame.quit()
        logging.info("pygame has been quit.")

if __name__ == "__main__":
    # Bluetooth speaker connection instructions
    logging.info("First, connect the Raspberry Pi to the Bluetooth speaker.")
    logging.info("Hold down the Bluetooth speaker button until you hear a sound to indicate it's ready to connect.")

    # Warning about running as sudo
    logging.info("Note: Do not run the program with sudo. Running as sudo can cause device configuration issues and errors.")
    logging.info("If the sound does not adjust or mute correctly, right-click the volume button on the top right of the Raspberry Pi 5 desktop screen and select 'Device Profile'.")

    joystick_control()
