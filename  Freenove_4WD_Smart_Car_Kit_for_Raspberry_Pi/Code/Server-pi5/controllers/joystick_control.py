# controllers/joystick_control.py

import time
import sys
import pygame
from Motor import Motor
from Ultrasonic import Ultrasonic
from Line_Tracking import Line_Tracking
from servo import Servo
from ADC import Adc
from Buzzer import Buzzer

def joystick_control():
    """
    ジョイスティックを使用して車とサーボを制御します。
    L1 Trigger (ボタン4): サーボ0を下に動かす
    R1 Trigger (ボタン5): サーボ0を上に動かす
    L2 Button (ボタン6): サーボ1を左に動かす
    R2 Button (ボタン7): サーボ1を右に動かす
    """
    try:
        # ハードウェアコンポーネントの初期化
        motor = Motor()
        ultrasonic = Ultrasonic()
        line_tracking = Line_Tracking()
        servo = Servo()
        adc = Adc()
        buzzer = Buzzer()

        # Pygameの初期化
        pygame.init()

        # ジョイスティックの初期化
        pygame.joystick.init()

        # 接続されているジョイスティックの数を取得
        joystick_count = pygame.joystick.get_count()
        print(f"接続されているジョイスティックの数: {joystick_count}")

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"ジョイスティック名: {joystick.get_name()}")
            print(f"軸の数: {joystick.get_numaxes()}")
            print(f"ボタンの数: {joystick.get_numbuttons()}")
            print(f"ハットの数: {joystick.get_numhats()}")
        else:
            print("ジョイスティックが接続されていません。プログラムを終了します。")
            pygame.quit()
            sys.exit()

        # デッドゾーンの定義
        DEAD_ZONE_MOVEMENT = 0.2
        DEAD_ZONE_ROTATION = 0.2

        # 最大PWM値
        MAX_PWM = 4095

        # サーボチャンネルの定義
        SERVO_NECK_CHANNEL = '0'          # サーボ0: 首の上下
        SERVO_LEFT_RIGHT_CHANNEL = '1'    # サーボ1: 左右

        # サーボ角度の定義
        SERVO_NECK_UP = 250                # 首を上に動かす角度
        SERVO_NECK_DOWN = 60               # 首を下に動かす角度
        SERVO_LEFT = -10                     # サーボ1を左に動かす角度
        SERVO_RIGHT = 120                  # サーボ1を右に動かす角度
        SERVO_NECK_NEUTRAL = 90            # 首の中立位置
        SERVO_LEFT_RIGHT_NEUTRAL = 90      # サーボ1の中立位置

        # プログラム開始時にサーボを中立位置に設定
        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
        servo.setServoPwm(SERVO_LEFT_RIGHT_CHANNEL, SERVO_LEFT_RIGHT_NEUTRAL)
        print("サーボを中立位置に設定しました。")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt  # ループを終了

                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    print(f"ボタン {button} が押されました。")

                    # Xboxコントローラーのボタンマッピング（コントローラーによって異なる場合があります）
                    if button == 4:  # L1 Trigger
                        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_DOWN)
                        print(f"サーボ0を下に {SERVO_NECK_DOWN} 度動かしました。")
                    elif button == 5:  # R1 Trigger
                        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_UP)
                        print(f"サーボ0を上に {SERVO_NECK_UP} 度動かしました。")
                    elif button == 6:  # L2 Button
                        servo.setServoPwm(SERVO_LEFT_RIGHT_CHANNEL, SERVO_LEFT)
                        print(f"サーボ1を左に {SERVO_LEFT} 度動かしました。")
                    elif button == 7:  # R2 Button
                        servo.setServoPwm(SERVO_LEFT_RIGHT_CHANNEL, SERVO_RIGHT)
                        print(f"サーボ1を右に {SERVO_RIGHT} 度動かしました。")

                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    print(f"ボタン {button} が離されました。")
                    # ボタンが離されたときにサーボを中立位置にリセット
                    if button in [4, 5]:  # サーボ0のボタン
                        servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
                        print("サーボ0を中立位置にリセットしました。")
                    if button in [6, 7]:  # サーボ1のボタン
                        servo.setServoPwm(SERVO_LEFT_RIGHT_CHANNEL, SERVO_LEFT_RIGHT_NEUTRAL)
                        print("サーボ1を中立位置にリセットしました。")

                elif event.type == pygame.JOYHATMOTION:
                    hat = event.hat
                    value = event.value
                    print(f"ハット {hat} が動きました。値: {value}")

            # ジョイスティックの軸を取得
            left_horizontal = joystick.get_axis(0)  # 左スティックX軸
            left_vertical = joystick.get_axis(1)    # 左スティックY軸

            # 回転用の右スティックの軸を取得
            right_horizontal = joystick.get_axis(3)  # 右スティックX軸
            # right_vertical = joystick.get_axis(4)    # 右スティックY軸（未使用）

            # 生の軸の値を表示
            raw_axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
            print(f"生の軸: {raw_axes}")

            # デッドゾーンを適用
            if abs(left_horizontal) < DEAD_ZONE_MOVEMENT:
                left_horizontal = 0
            if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                left_vertical = 0
            if abs(right_horizontal) < DEAD_ZONE_ROTATION:
                right_horizontal = 0

            # 移動方向を計算
            y = -left_vertical
            x = left_horizontal

            # 回転を計算
            rotation = right_horizontal  # 右スティックX軸を回転に使用

            # 回転の強度を調整
            rotation_strength = rotation * 0.5  # 回転を半分にスケール

            # モーターコマンドを計算
            front_left = y + x + rotation_strength
            front_right = y - x - rotation_strength
            back_left = y - x + rotation_strength
            back_right = y + x - rotation_strength

            # モーターコマンドを正規化（-1から1の範囲）
            max_val = max(abs(front_left), abs(front_right), abs(back_left), abs(back_right), 1)
            front_left /= max_val
            front_right /= max_val
            back_left /= max_val
            back_right /= max_val

            # PWM値に変換（-4095から4095）
            duty_front_left = int(front_left * MAX_PWM)
            duty_front_right = int(front_right * MAX_PWM)
            duty_back_left = int(back_left * MAX_PWM)
            duty_back_right = int(back_right * MAX_PWM)

            # PWM値を表示
            print(f"PWM値 - FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

            # モーターにPWM値を送信
            motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right)

            # 短い期間待機
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
        try:
            # モーターを停止
            motor.setMotorModel(0, 0, 0, 0)
            # サーボを中立位置にリセット
            servo.setServoPwm(SERVO_NECK_CHANNEL, SERVO_NECK_NEUTRAL)
            servo.setServoPwm(SERVO_LEFT_RIGHT_CHANNEL, SERVO_LEFT_RIGHT_NEUTRAL)
        except Exception as e:
            print(f"モーター停止またはサーボリセット中にエラーが発生しました: {e}")
        finally:
            pygame.quit()
        sys.exit()

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        pygame.quit()
        sys.exit()
