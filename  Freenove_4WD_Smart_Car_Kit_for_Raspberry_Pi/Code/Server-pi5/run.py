# run.py

import threading
import sys
import logging
from controllers.joystick_control import joystick_control
from controllers.camera_control import camera_control

# Configure logging for the main thread
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    # Create joystick control thread
    joystick_thread = threading.Thread(target=joystick_control, name='JoystickControlThread')
    
    # Create camera control thread
    camera_thread = threading.Thread(target=camera_control, name='CameraControlThread')
    
    # Start joystick control thread as daemon (it will terminate when the main thread exits)
    joystick_thread.daemon = True
    joystick_thread.start()
    logging.info("Joystick control thread started.")
    
    # Start camera control thread as daemon
    camera_thread.daemon = True
    camera_thread.start()
    logging.info("Camera control thread started.")
    
    # Keep the main thread alive to allow daemon threads to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nExiting program gracefully.")
    finally:
        logging.info("Terminating program.")
        sys.exit()

if __name__ == '__main__':
    main()
