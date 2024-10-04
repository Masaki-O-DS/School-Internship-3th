# controllers/camera_control.py

import cv2
from cv2 import aruco
from picamera2 import Picamera2, Preview
import time

def camera_control():
    """
    Continuously captures video from the camera, detects AR markers, and displays the result.
    Press 'q' to exit the camera feed.
    """
    try:
        # Initialize Picamera2
        picam2 = Picamera2()
        # Use a 3-channel RGB format to ensure compatibility with OpenCV
        preview_config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
        picam2.configure(preview_config)
        picam2.start()
        # print("Camera started successfully.")

        # Initialize ARUCO dictionary and parameters
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)  # 4x4 bit ARUCO markers
        parameters = aruco.DetectorParameters_create()

        while True:
            # Capture frame from the camera
            frame = picam2.capture_array()

            # Validate the captured frame
            if frame is None or frame.size == 0:
                # print("Empty frame captured. Skipping frame processing.")
                continue

            # Check if the frame has the correct number of channels (3 for RGB)
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                # print(f"Unexpected frame shape: {frame.shape}. Expected 3 channels (RGB). Skipping frame.")
                continue

            # Convert frame to grayscale for ARUCO detection
            # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Detect ARUCO markers in the grayscale frame
            corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

            # Draw detected markers on the original frame
            # if ids is not None:
            #     frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
            # else:
            #     frame_markers = frame.copy()
            if ids is not None:
                frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                frame_markers = aruco.drawDetectedMarkers(frame_color, corners, ids)
            else:
                frame_markers = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # Display the frame with detected markers
            cv2.imshow("AR Marker Detection", frame_markers)

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # print("Stopping camera feed.")
                break

            # Short delay to reduce CPU usage
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nExiting camera program gracefully.")
    except Exception as e:
        print(f"An unexpected error occurred in camera_control: {e}")
    finally:
        # Ensure that the camera is stopped and all OpenCV windows are closed
        picam2.stop()
        cv2.destroyAllWindows()
        # print("Camera and OpenCV windows have been closed.")
