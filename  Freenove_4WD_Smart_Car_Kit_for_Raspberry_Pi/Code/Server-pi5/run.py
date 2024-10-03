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

    print("Started joystick control and camera control.")

    try:
        # Main thread waits for threads to finish
        while True:
            if not joystick_thread.is_alive() or not camera_thread.is_alive():
                print("One of the threads has stopped. Exiting program.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        print("All threads have been terminated.")
        sys.exit()

if __name__ == '__main__':
    main()
