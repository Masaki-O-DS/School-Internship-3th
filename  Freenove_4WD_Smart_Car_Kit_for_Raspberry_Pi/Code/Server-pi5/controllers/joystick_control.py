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
    def __init__(self, sound_file='/home/ogawamasaki/School-Internship-3th-Car/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav', volume=0.7):
        # Prevent running as sudo
        if os.geteuid() == 0:
            logging.error("Running as sudo is not allowed.")
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
    Continuously captures video from the camera, detects AR markers, and displays the result.
    Press 'q' to exit the camera feed.
    Implements frame rate monitoring and uses an optimal pixel format for efficiency.
    """
    picam2 = None  # Ensure picam2 is defined before the try block

    try:
        # Initialize Picamera2
        picam2 = Picamera2()

        # Use RGB888 format for better compatibility with OpenCV
        resolution = (640, 480)  # Lower resolution for better performance
        preview_config = picam2.create_preview_configuration(
            main={"format": 'RGB888', "size": resolution}
        )
        picam2.configure(preview_config)
        picam2.start()
        logging.info("Camera started successfully.")

        # Initialize ARUCO dictionary and parameters
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)  # 4x4 bit ARUCO markers
        parameters = aruco.DetectorParameters_create()
        parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX  # Improve corner accuracy

        # Initialize buzzer
        buzzer = Buzzer()

        # Initialize variables for FPS calculation
        frame_count = 0
        start_time = time.time()
        fps = 0

        def update_fps():
            nonlocal frame_count, start_time, fps
            while True:
                time.sleep(0.2)  # Update FPS more frequently
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    fps = frame_count / elapsed_time
                    logging.info(f"FPS: {fps:.2f}")
                    frame_count = 0
                    start_time = time.time()

        # Start a thread to update FPS
        fps_thread = threading.Thread(target=update_fps, daemon=True)
        fps_thread.start()

        while True:
            # Capture frame from the camera
            frame = picam2.capture_array()

            # Validate the captured frame
            if frame is None or frame.size == 0:
                logging.warning("Empty frame captured. Skipping frame processing.")
                continue

            # Convert frame to grayscale for ARUCO detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Detect ARUCO markers in the grayscale frame
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            # Draw detected markers on the original frame
            if ids is not None:
                frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
                # Save the frame when AR marker is detected
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"aruco_detected_{timestamp}.png"
                cv2.imwrite(filename, frame_markers)
                logging.info(f"AR marker detected. Image saved as {filename}")
                # Play buzzer sound
                buzzer.run('1')
            else:
                frame_markers = frame.copy()

            # Display the frame with detected markers in a single window
            cv2.imshow("AR Marker Detection", frame_markers)

            # Increment frame count for FPS calculation
            frame_count += 1

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Stopping camera feed.")
                break

    except KeyboardInterrupt:
        logging.info("\nExiting camera program gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in camera_control: {e}")
    finally:
        # Ensure that the camera is stopped and all OpenCV windows are closed
        if picam2 is not None:
            picam2.stop()
        cv2.destroyAllWindows()
        logging.info("Camera and OpenCV windows have been closed.")

if __name__ == "__main__":
    joystick_control()