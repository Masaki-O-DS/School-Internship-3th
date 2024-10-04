# controllers/camera_control.py

import cv2
from cv2 import aruco
from picamera2 import Picamera2
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def camera_control():
    """
    Continuously captures video from the camera, detects AR markers, and displays the result.
    Press 'q' to exit the camera feed.
    """
    try:
        # Initialize Picamera2
        picam2 = Picamera2()
        # Use a 3-channel RGB format with a reasonable resolution for real-time processing
        resolution = (640, 480)  # Adjust as needed for performance
        preview_config = picam2.create_video_configuration(main={"format": 'RGB888', "size": resolution})
        picam2.configure(preview_config)
        picam2.start()
        logging.info("Camera started successfully.")

        # Initialize ARUCO dictionary and parameters
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)  # 4x4 bit ARUCO markers
        parameters = aruco.DetectorParameters_create()
        parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX  # Improve corner accuracy

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
                frame_markers = aruco.drawDetectedMarkers(frame, corners, ids)
            else:
                frame_markers = frame

            # Display the frame with detected markers
            cv2.imshow("AR Marker Detection", frame_markers)

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Stopping camera feed.")
                break

            # Optional: Remove sleep to maximize frame rate
            # time.sleep(0.01)  # Adjust or remove as needed

    except KeyboardInterrupt:
        logging.info("\nExiting camera program gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in camera_control: {e}")
    finally:
        # Ensure that the camera is stopped and all OpenCV windows are closed
        picam2.stop()
        cv2.destroyAllWindows()
        logging.info("Camera and OpenCV windows have been closed.")
