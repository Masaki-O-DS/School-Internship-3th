import time
import sys
import pygame
from Motor import Motor
from Ultrasonic import Ultrasonic
from Line_Tracking import Line_Tracking
from servo import Servo
from ADC import Adc
from Buzzer import Buzzer

# Initialize hardware components
PWM = Motor()
ultrasonic = Ultrasonic()
line = Line_Tracking()
pwm_servo = Servo()
adc = Adc()
buzzer = Buzzer()

def test_Motor():
    try:
        PWM.setMotorModel(1000, 1000, 1000, 1000)         # Forward
        print("The car is moving forward")
        time.sleep(1)
        PWM.setMotorModel(-1000, -1000, -1000, -1000)     # Backward
        print("The car is going backwards")
        time.sleep(1)
        PWM.setMotorModel(-1500, -1500, 2000, 2000)       # Turn left
        print("The car is turning left")
        time.sleep(1)
        PWM.setMotorModel(2000, 2000, -1500, -1500)       # Turn right 
        print("The car is turning right")  
        time.sleep(1)
        PWM.setMotorModel(-2000, 2000, 2000, -2000)       # Move left 
        print("The car is moving left")  
        time.sleep(1)
        PWM.setMotorModel(2000, -2000, -2000, 2000)       # Move right 
        print("The car is moving right")  
        time.sleep(1)    
            
        PWM.setMotorModel(0, 2000, 2000, 0)               # Diagonal left forward
        print("The car is moving diagonally to the left and forward")  
        time.sleep(1)
        PWM.setMotorModel(0, -2000, -2000, 0)             # Diagonal right backward
        print("The car is moving diagonally to the right and backward")  
        time.sleep(1) 
        PWM.setMotorModel(2000, 0, 0, 2000)               # Diagonal right forward
        print("The car is moving diagonally to the right and forward")  
        time.sleep(1)
        PWM.setMotorModel(-2000, 0, 0, -2000)             # Diagonal left backward
        print("The car is moving diagonally to the left and backward")  
        time.sleep(1) 
        
        PWM.setMotorModel(0, 0, 0, 0)                     # Stop
        print("\nEnd of program")
    except KeyboardInterrupt:
        PWM.setMotorModel(0, 0, 0, 0)
        print("\nEnd of program")

def test_Ultrasonic():
    try:
        while True:
            data = ultrasonic.get_distance()   # Get distance
            print(f"Obstacle distance is {data} CM")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEnd of program")

def car_Rotate():
    try:
        while True:
            PWM.Rotate(0)
    except KeyboardInterrupt:
        print("\nEnd of program")

def test_Infrared():
    try:
        line.test_Infrared()
    except KeyboardInterrupt:
        print("\nEnd of program")

def test_Servo():
    try:
        while True:
            for i in range(50, 110, 1):
                pwm_servo.setServoPwm('0', i)
                print(f"Servo 0 set to {i} degrees")
                time.sleep(0.01)
            for i in range(110, 50, -1):
                pwm_servo.setServoPwm('0', i)
                print(f"Servo 0 set to {i} degrees")
                time.sleep(0.01)
            for i in range(80, 150, 1):
                pwm_servo.setServoPwm('1', i)
                print(f"Servo 1 set to {i} degrees")
                time.sleep(0.01)
            for i in range(150, 80, -1):
                pwm_servo.setServoPwm('1', i)
                print(f"Servo 1 set to {i} degrees")
                time.sleep(0.01)   
    except KeyboardInterrupt:
        pwm_servo.setServoPwm('0', 90)
        pwm_servo.setServoPwm('1', 90)
        print("\nEnd of program")

def test_Adc():
    try:
        while True:
            Left_IDR = adc.recvADC(0)
            print(f"The photoresistor voltage on the left is {Left_IDR} V")
            Right_IDR = adc.recvADC(1)
            print(f"The photoresistor voltage on the right is {Right_IDR} V")
            Power = adc.recvADC(2)
            print(f"The battery voltage is {Power * 3} V")
            time.sleep(1)
            print('\n')
    except KeyboardInterrupt:
        print("\nEnd of program")

def test_Buzzer():
    try:
        buzzer.run('1')
        time.sleep(1)
        print("1S")
        time.sleep(1)
        print("2S")
        time.sleep(1)
        print("3S")
        buzzer.run('0')
        print("\nEnd of program")
    except KeyboardInterrupt:
        buzzer.run('0')
        print("\nEnd of program")
           
def control_Neck_With_Pygame():
    """
    Controls the neck servo (assumed to be Servo 0) using Pygame keyboard inputs.
    Up Arrow: Move neck up
    Down Arrow: Move neck down
    Press Esc or close the window to exit
    """
    try:
        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('Neck Control')
        font = pygame.font.Font(None, 36)
        clock = pygame.time.Clock()

        # Initial servo position
        servo_channel = '0'  # Assuming Servo 0 controls the neck
        position = 90  # Starting at neutral position

        # Define movement increment
        increment = 20

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        position += increment
                        if position > 180:
                            position = 180
                        pwm_servo.setServoPwm(servo_channel, position)
                        print(f"Neck moved up to {position} degrees")
                    elif event.key == pygame.K_DOWN:
                        position -= increment
                        if position < 0:
                            position = 0
                        pwm_servo.setServoPwm(servo_channel, position)
                        print(f"Neck moved down to {position} degrees")

            # Update the Pygame window
            screen.fill((255, 255, 255))
            text = font.render(f"Neck Position: {position}°", True, (0, 0, 0))
            screen.blit(text, (50, 130))
            pygame.display.flip()
            clock.tick(30)

        # Reset servo to neutral position on exit
        pwm_servo.setServoPwm(servo_channel, 90)
        print("Neck reset to 90 degrees. Exiting...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()



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
        SERVO_NECK_UP = 170                # Increased upward angle
        SERVO_NECK_DOWN = 60               # Downward angle
        SERVO_LEFT = 60                    # Left position for Servo 1
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
                            print("Servo 0 moved down.")
                        elif button == 5:  # R1 Trigger
                            pwm_servo.setServoPwm(servo_channel_neck, SERVO_NECK_UP)
                            print("Servo 0 moved up.")
                        elif button == 6:  # L2 Button
                            pwm_servo.setServoPwm(servo_channel_left_right, SERVO_LEFT)
                            print("Servo 1 moved to the left.")
                        elif button == 7:  # R2 Button
                            pwm_servo.setServoPwm(servo_channel_left_right, SERVO_RIGHT)
                            print("Servo 1 moved to the right.")

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

                # Convert to PWM values (0 to 4095)
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

# Main program logic:
if __name__ == '__main__':

    print('Program is starting...')
    if len(sys.argv) < 2:
        print("Parameter error: Please assign the device")
        print("Available devices: Led, Motor, Ultrasonic, Infrared, Servo, ADC, Buzzer, Rotate, Neck, Joystick")
        sys.exit()

    device = sys.argv[1]

    if device == 'Led':
        # Ensure you have a test_Led function defined
        try:
            from Led import *
            test_Led()
        except ImportError:
            print("Led module not found.")
    elif device == 'Motor':
        test_Motor()
    elif device == 'Ultrasonic':
        test_Ultrasonic()
    elif device == 'Infrared':
        test_Infrared()        
    elif device == 'Servo': 
        test_Servo()               
    elif device == 'ADC':   
        test_Adc()  
    elif device == 'Buzzer':   
        test_Buzzer()  
    elif device == 'Rotate':
        car_Rotate()
    elif device == 'Neck':
        control_Neck_With_Pygame()
    elif device == 'Joystick':
        joystick_Control()
    else:
        print(f"Unknown device: {device}")
        print("Available devices: Led, Motor, Ultrasonic, Infrared, Servo, ADC, Buzzer, Rotate, Neck, Joystick")
