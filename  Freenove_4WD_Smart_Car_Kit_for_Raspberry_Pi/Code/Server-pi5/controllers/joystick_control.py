
# controllers/joystick_control.py

import time
import sys
import pygame
from Motor import Motor
from servo import Servo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def joystick_control():
    """
    Controls the car and Servo0 (neck) using a joystick.
    L1 Trigger (Button 4): Move Servo0 downward
    R1 Trigger (Button 5): Move Servo0 upward
    """

    try:
        # Initialize hardware components
        motor = Motor()
        servo = Servo()

        # Initialize Pygame
        pygame.init()

        # Initialize joystick
        pygame.joystick.init()

        # Get the number of connected joysticks
        joystick_count = pygame.joystick.get_count()
        logging.info(f"Number of joysticks connected: {joystick_count}")

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            logging.info(f"Joystick name: {joystick.get_name()}")
            logging.info(f"Number of axes: {joystick.get_numaxes()}")
            logging.info(f"Number of buttons: {joystick.get_numbuttons()}")
            logging.info(f"Number of hats: {joystick.get_numhats()}")
        else:
            logging.error("No joysticks connected. Exiting program.")
            pygame.quit()
            sys.exit()

        # Define dead zones
        DEAD_ZONE_MOVEMENT = 0.2

        # Maximum PWM value
        MAX_PWM = 4095

        # Define servo channel
        SERVO_NECK_CHANNEL = '1'          # Servo0: neck up/down

        # Define servo angles within 0° to 180°
        SERVO_NECK_UP = 160                # Move neck up
        SERVO_NECK_DOWN = 120              # Move neck down
        SERVO_NECK_NEUTRAL = 90            # Neutral position for neck servo

        # Set servo to neutral position at start
        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
        logging.info("Servo0 set to neutral position.")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt  # Exit loop

                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    logging.info(f"Button {button} pressed.")

                    # Xbox Controller Button Mapping (may vary depending on controller)
                    if button == 6:  # L1 Trigger
                        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_DOWN)
                        logging.info(f"Servo0 moved down to {SERVO_NECK_DOWN} degrees.")
                    elif button == 7:  # R1 Trigger
                        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_UP)
                        logging.info(f"Servo0 moved up to {SERVO_NECK_UP} degrees.")

                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    # Reset Servo0 to neutral when buttons are released
                    if button in [4, 5]:  # Servo0 buttons
                        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
                        logging.info("Servo0 reset to neutral position.")

                elif event.type == pygame.JOYHATMOTION:
                    hat = event.hat
                    value = event.value
                    logging.info(f"Hat {hat} moved. Value: {value}")

            # Get joystick axes
            left_vertical = joystick.get_axis(1)    # Left stick Y-axis

            # Display raw axis values
            raw_axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
            logging.info(f"Raw axes: {raw_axes}")

            # Apply dead zone
            if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                left_vertical = 0

            # Calculate movement direction
            y = -left_vertical  # Invert axis for intuitive control

            # Convert to PWM values (-4095 to 4095)
            duty = int(y * MAX_PWM)

            # Set all motors to the same PWM value for forward/backward movement
            duty_front_left = duty
            duty_front_right = duty
            duty_back_left = duty
            duty_back_right = duty

            # Display PWM values
            logging.info(f"PWM values - FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

            # Send PWM values to motors
            motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right)

            # Short wait to prevent excessive CPU usage
            time.sleep(0.05)

    except KeyboardInterrupt:
        logging.info("\nExiting program.")
        try:
            # Stop motors
            motor.setMotorModel(0, 0, 0, 0)
            # Reset servo to neutral position
            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
            logging.info("Motors stopped and Servo0 reset to neutral position.")
        except Exception as e:
            logging.error(f"Error while stopping motors or resetting servo: {e}")
        finally:
            pygame.quit()
        sys.exit()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()
