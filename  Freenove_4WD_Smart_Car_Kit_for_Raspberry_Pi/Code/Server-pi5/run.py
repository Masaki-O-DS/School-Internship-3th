def joystick_Control():
    """
    Controls the car and servos using a joystick.
    L1 Trigger: Move Servo 0 downward
    R1 Trigger: Move Servo 0 upward
    L2 Button: Move Servo 1 to the left
    R2 Button: Move Servo 1 to the right
    """
    try:
        # Initialize Pygame
        pygame.init()

        # Initialize joystick
        pygame.joystick.init()

        # Get the number of joysticks
        joystick_count = pygame.joystick.get_count()
        print(f"Number of joysticks connected: {joystick_count}")

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Joystick name: {joystick.get_name()}")
            print(f"Number of axes: {joystick.get_numaxes()}")
            print(f"Number of buttons: {joystick.get_numbuttons()}")
            print(f"Number of hats: {joystick.get_numhats()}")
        else:
            print("No joysticks connected. Exiting program.")
            pygame.quit()
            sys.exit()

        # Initialize Motor
        motor = Motor()

        # Define dead zones
        DEAD_ZONE_MOVEMENT = 0.2
        DEAD_ZONE_ROTATION = 0.2

        # Maximum PWM value
        MAX_PWM = 4095

        # Define servo channels
        servo_channel_neck = '0'          # Servo 0 controls neck up/down
        servo_channel_left_right = '1'    # Servo 1 controls left/right

        # Define servo angles
        SERVO_NECK_UP = 175                # Adjusted upward angle
        SERVO_NECK_DOWN = 60               # Downward angle
        SERVO_LEFT = 10                    # Further left position for Servo 1
        SERVO_RIGHT = 120                  # Right position for Servo 1
        SERVO_NECK_NEUTRAL = 90            # Neutral position for Servo 0
        SERVO_LEFT_RIGHT_NEUTRAL = 90      # Neutral position for Servo 1

        # Set servos to neutral position at start
        pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_NEUTRAL)
        pwm_servo.setServoPwm(servo_channel_left_right, SERVO_LEFT_RIGHT_NEUTRAL)
        print("Servos set to neutral positions.")

        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt  # Exit the loop

                    elif event.type == pygame.JOYBUTTONDOWN:
                        button = event.button
                        print(f"Button {button} pressed.")

                        # Xbox Controller Button Mapping (may vary)
                        if button == 4:  # L1 Trigger
                            pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_DOWN)
                            print(f"Servo 0 moved down to {SERVO_NECK_DOWN} degrees.")
                        elif button == 5:  # R1 Trigger
                            pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_UP)
                            print(f"Servo 0 moved up to {SERVO_NECK_UP} degrees.")
                        elif button == 6:  # L2 Button
                            pwm_servo.setServoPwm(servo_channel_left_right, SERVO_LEFT)
                            print(f"Servo 1 moved to the left to {SERVO_LEFT} degrees.")
                        elif button == 7:  # R2 Button
                            pwm_servo.setServoPwm(servo_channel_left_right, SERVO_RIGHT)
                            print(f"Servo 1 moved to the right to {SERVO_RIGHT} degrees.")

                    elif event.type == pygame.JOYBUTTONUP:
                        button = event.button
                        print(f"Button {button} released.")
                        # Reset servos to neutral when buttons are released
                        if button == 4:  # L1 Trigger released
                            pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_NEUTRAL)
                            print("Servo 0 reset to neutral.")
                        elif button == 5:  # R1 Trigger released
                            pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_NEUTRAL)
                            print("Servo 0 reset to neutral.")
                        elif button == 6:  # L2 Button released
                            pwm_servo.setServoPwm(servo_channel_left_right, SERVO_LEFT_RIGHT_NEUTRAL)
                            print("Servo 1 reset to neutral.")
                        elif button == 7:  # R2 Button released
                            pwm_servo.setServoPwm(servo_channel_left_right, SERVO_LEFT_RIGHT_NEUTRAL)
                            print("Servo 1 reset to neutral.")

                    elif event.type == pygame.JOYHATMOTION:
                        hat = event.hat
                        value = event.value
                        print(f"Hat {hat} moved. Value: {value}")

                # Get joystick axes for movement
                left_horizontal = joystick.get_axis(0)  # Left stick X-axis
                left_vertical = joystick.get_axis(1)    # Left stick Y-axis

                # Get joystick axes for rotation
                right_horizontal = joystick.get_axis(3)  # Right stick X-axis
                # right_vertical = joystick.get_axis(4)    # Right stick Y-axis (unused)

                # Display raw axes values
                raw_axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
                print(f"Raw axes: {raw_axes}")

                # Apply dead zones
                if abs(left_horizontal) < DEAD_ZONE_MOVEMENT:
                    left_horizontal = 0
                if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                    left_vertical = 0
                if abs(right_horizontal) < DEAD_ZONE_ROTATION:
                    right_horizontal = 0
                # if abs(right_vertical) < DEAD_ZONE_ROTATION:
                #     right_vertical = 0

                # Calculate movement direction
                y = -left_vertical
                x = left_horizontal

                # Calculate rotation
                rotation = right_horizontal  # Use right stick X-axis for rotation

                # Adjust rotation strength
                rotation_strength = rotation * 0.5  # Scale rotation

                # Calculate motor commands
                front_left = y + x + rotation_strength
                front_right = y - x - rotation_strength
                back_left = y - x + rotation_strength
                back_right = y + x - rotation_strength

                # Normalize motor commands to range [-1, 1]
                max_val = max(abs(front_left), abs(front_right), abs(back_left), abs(back_right), 1)
                front_left /= max_val
                front_right /= max_val
                back_left /= max_val
                back_right /= max_val

                # Convert to PWM values (-4095 to 4095)
                duty_front_left = int(front_left * MAX_PWM)
                duty_front_right = int(front_right * MAX_PWM)
                duty_back_left = int(back_left * MAX_PWM)
                duty_back_right = int(back_right * MAX_PWM)

                # Display PWM values
                print(f"PWM values - FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

                # Send PWM values to motors
                motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right)

                # Wait for a short period
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nExiting program.")
        # Stop motors
        motor.setMotorModel(0, 0, 0, 0)
        # Reset servos to neutral positions
        pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_NEUTRAL)
        pwm_servo.setServoPwm(servo_channel_left_right, SERVO_LEFT_RIGHT_NEUTRAL)
        sys.exit()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()
