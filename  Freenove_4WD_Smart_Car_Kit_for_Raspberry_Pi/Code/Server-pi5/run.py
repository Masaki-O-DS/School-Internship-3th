# run.py

import threading
import time
import sys
from controllers.joystick_control import joystick_control
from controllers.camera_control import camera_control

def main():
    # Create joystick control thread
    joystick_thread = threading.Thread(target=joystick_control, name='JoystickControlThread')
    
    # Create camera control thread
    camera_thread = threading.Thread(target=camera_control, name='CameraControlThread')
    
    # Start threads as daemon (they will terminate when the main thread exits)
    joystick_thread.daemon = True
    camera_thread.daemon = True
    
    joystick_thread.start()
    camera_thread.start()
    
    print("Joystick control and camera control have been started.")
    
    try:
        # Main thread waits for both threads to finish
        while True:
            # Check if any thread has stopped unexpectedly
            if not joystick_thread.is_alive():
                print("Joystick control thread has stopped unexpectedly. Exiting program.")
                break
            if not camera_thread.is_alive():
                print("Camera control thread has stopped unexpectedly. Exiting program.")
                break
            # Sleep to reduce CPU usage
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting program gracefully.")
    finally:
        print("All threads have been terminated.")
        sys.exit()

if __name__ == '__main__':
    main()
