# run.py

import threading
import time
import sys
from controllers.joystick_control import joystick_control
from controllers.camera_control import camera_control

def main():
    # Create joystick control thread
    joystick_thread = threading.Thread(target=joystick_control, name='JoystickControlThread')
    
    # Start joystick control thread as daemon (it will terminate when the main thread exits)
    joystick_thread.daemon = True
    joystick_thread.start()
    
    
    # Run camera_control in the main thread
    try:
        camera_control()
    except KeyboardInterrupt:
        print("\nExiting program gracefully.")
    finally:
        print("Terminating program.")
        sys.exit()

if __name__ == '__main__':
    main()
