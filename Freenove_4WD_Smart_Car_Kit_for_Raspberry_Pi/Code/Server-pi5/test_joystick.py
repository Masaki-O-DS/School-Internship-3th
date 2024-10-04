import pygame
import sys
import time
from Motor import Motor

def main():
    # Pygame????
    pygame.init()

    # ?????????????????
    pygame.joystick.init()

    # ?????????????
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

    # ????????
    motor = Motor()

    # ?????????
    DEAD_ZONE_MOVEMENT = 0.2
    DEAD_ZONE_ROTATION = 0.2

    # ??PWM?
    MAX_PWM = 4095

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt  # ????????

                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    print(f"Button {button} pressed.")

                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    print(f"Button {button} released.")

                elif event.type == pygame.JOYHATMOTION:
                    hat = event.hat
                    value = event.value
                    print(f"Hat {hat} moved. Value: {value}")

            # ?????????????
            # ??????
            left_horizontal = joystick.get_axis(0)  # ??????
            left_vertical = joystick.get_axis(1)    # ??????

            # ??????
            right_horizontal = joystick.get_axis(3)  # ??????
            # right_vertical = joystick.get_axis(4)    # ?????? ?????????

            # ????: ???????
            raw_axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
            print(f"Raw axes: {raw_axes}")

            # ?????????
            if abs(left_horizontal) < DEAD_ZONE_MOVEMENT:
                left_horizontal = 0
            if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                left_vertical = 0
            if abs(right_horizontal) < DEAD_ZONE_ROTATION:
                right_horizontal = 0
            # if abs(right_vertical) < DEAD_ZONE_ROTATION:
            #     right_vertical = 0

            # ?????????????
            # ?????????????????????????
            y = -left_vertical
            x = left_horizontal

            # ?????
            rotation = right_horizontal  # ???????????????

            # ?????????????????????
            rotation_strength = rotation * 0.5  # 0.5?????????

            # ?????????
            front_left = y + x + rotation_strength
            front_right = y - x - rotation_strength
            back_left = y - x + rotation_strength
            back_right = y + x - rotation_strength

            # ????-1??1????????
            max_val = max(abs(front_left), abs(front_right), abs(back_left), abs(back_right), 1)
            front_left /= max_val
            front_right /= max_val
            back_left /= max_val
            back_right /= max_val

            # PWM?????????????-4095??4095?
            duty_front_left = int(front_left * MAX_PWM)
            duty_front_right = int(front_right * MAX_PWM)
            duty_back_left = int(back_left * MAX_PWM)
            duty_back_right = int(back_right * MAX_PWM)

            # ?????????
            print(f"PWM values - FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

            # ?????????????????
            motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right)

            # ?????
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nExiting program.")
        # ???????
        motor.setMotorModel(0, 0, 0, 0)
        sys.exit()

if __name__ == "__main__":
    main()
