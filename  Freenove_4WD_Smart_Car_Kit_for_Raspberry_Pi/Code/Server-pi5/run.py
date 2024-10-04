# run.py
import threading
import sys
import logging
import time
from controllers.joystick_control import joystick_control
from controllers.camera_control import camera_control

# Configure logging for the main thread
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    # Create joystick control thread
    joystick_thread = threading.Thread(target=joystick_control, name='JoystickControlThread')
    
    # Create camera control thread
    camera_thread = threading.Thread(target=camera_control, name='CameraControlThread')
    
    # Start threads as non-daemon (they won't automatically terminate when the main thread exits)
    joystick_thread.start()
    logging.info("Joystick control thread started.")
    
    camera_thread.start()
    logging.info("Camera control thread started.")
    
    # Keep the main thread alive to allow threads to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nExiting program gracefully.")
    finally:
        # Set a flag or use an event to signal threads to stop
        # Wait for threads to finish
        joystick_thread.join()
        camera_thread.join()
        logging.info("All threads have finished. Terminating program.")
        sys.exit()

if __name__ == '__main__':
    main()