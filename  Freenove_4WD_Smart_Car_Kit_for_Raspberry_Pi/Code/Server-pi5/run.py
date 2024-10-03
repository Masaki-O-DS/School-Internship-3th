import time
import sys
import pygame
from Motor import Motor
from Ultrasonic import Ultrasonic
from Line_Tracking import Line_Tracking
from servo import Servo
from ADC import Adc
from Buzzer import Buzzer

# ハードウェアコンポーネントの初期化
PWM = Motor()
ultrasonic = Ultrasonic()
line = Line_Tracking()
pwm_servo = Servo()
adc = Adc()
buzzer = Buzzer()

def test_Motor():
    try:
        PWM.setMotorModel(1000,1000,1000,1000)         # 前進
        print ("The car is moving forward")
        time.sleep(1)
        PWM.setMotorModel(-1000,-1000,-1000,-1000)     # 後退
        print ("The car is going backwards")
        time.sleep(1)
        PWM.setMotorModel(-1500,-1500,2000,2000)       # 左折
        print ("The car is turning left")
        time.sleep(1)
        PWM.setMotorModel(2000,2000,-1500,-1500)       # 右折 
        print ("The car is turning right")  
        time.sleep(1)
        PWM.setMotorModel(-2000,2000,2000,-2000)       # 左移動 
        print ("The car is moving left")  
        time.sleep(1)
        PWM.setMotorModel(2000,-2000,-2000,2000)       # 右移動 
        print ("The car is moving right")  
        time.sleep(1)    
            
        PWM.setMotorModel(0,2000,2000,0)         # 左前斜め移動
        print ("The car is moving diagonally to the left and forward")  
        time.sleep(1)
        PWM.setMotorModel(0,-2000,-2000,0)       # 右後斜め移動
        print ("The car is moving diagonally to the right and backward")  
        time.sleep(1) 
        PWM.setMotorModel(2000,0,0,2000)         # 右前斜め移動
        print ("The car is moving diagonally to the right and forward")  
        time.sleep(1)
        PWM.setMotorModel(-2000,0,0,-2000)       # 左後斜め移動
        print ("The car is moving diagonally to the left and backward")  
        time.sleep(1) 
        
        PWM.setMotorModel(0,0,0,0)               # 停止
        print ("\nEnd of program")
    except KeyboardInterrupt:
        PWM.setMotorModel(0,0,0,0)
        print ("\nEnd of program")

def test_Ultrasonic():
    try:
        while True:
            data = ultrasonic.get_distance()   # 距離取得
            print ("Obstacle distance is "+str(data)+"CM")
            time.sleep(1)
    except KeyboardInterrupt:
        print ("\nEnd of program")

def car_Rotate():
    try:
        while True:
            PWM.Rotate(0)
    except KeyboardInterrupt:
        print ("\nEnd of program")

def test_Infrared():
    try:
        line.test_Infrared()
    except KeyboardInterrupt:
        print ("\nEnd of program")

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
        print ("\nEnd of program")

def test_Adc():
    try:
        while True:
            Left_IDR = adc.recvADC(0)
            print ("The photoresistor voltage on the left is "+str(Left_IDR)+"V")
            Right_IDR = adc.recvADC(1)
            print ("The photoresistor voltage on the right is "+str(Right_IDR)+"V")
            Power = adc.recvADC(2)
            print ("The battery voltage is "+str(Power*3)+"V")
            time.sleep(1)
            print ('\n')
    except KeyboardInterrupt:
        print ("\nEnd of program")

def test_Buzzer():
    try:
        buzzer.run('1')
        time.sleep(1)
        print ("1S")
        time.sleep(1)
        print ("2S")
        time.sleep(1)
        print ("3S")
        buzzer.run('0')
        print ("\nEnd of program")
    except KeyboardInterrupt:
        buzzer.run('0')
        print ("\nEnd of program")

def control_Neck_With_Pygame():
    """
    Pygameのキーボード入力を使用して首のサーボ（サーボ0と仮定）を制御します。
    上矢印キー: 首を上に動かす
    下矢印キー: 首を下に動かす
    Escキーまたはウィンドウを閉じると終了
    """
    try:
        # Pygameの初期化
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('Neck Control')
        font = pygame.font.Font(None, 36)
        clock = pygame.time.Clock()

        # 初期サーボ位置
        servo_channel = '0'  # サーボ0が首を制御すると仮定
        position = 90  # 中立位置から開始

        # 移動量の定義
        increment = 5

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

            # Pygameウィンドウの更新
            screen.fill((255, 255, 255))
            text = font.render(f"Neck Position: {position}°", True, (0, 0, 0))
            screen.blit(text, (50, 130))
            pygame.display.flip()
            clock.tick(30)

        # 終了時にサーボを中立位置にリセット
        pwm_servo.setServoPwm(servo_channel, 90)
        print("Neck reset to 90 degrees. Exiting...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

def main():
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

    # モーターの初期化
    motor = Motor()

    # デッドゾーンの設定
    DEAD_ZONE_MOVEMENT = 0.2
    DEAD_ZONE_ROTATION = 0.2

    # PWMの最大値
    MAX_PWM = 4095

    # サーボ制御用変数
    servo_channel_neck = '0'  # 首を制御するサーボのチャンネル
    servo_channel_left_right = '1'  # 左右を制御するサーボのチャンネル

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt  # プログラム終了

                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    print(f"ボタン {button} が押されました。")

                    # ボタンのマッピング（ジョイスティックによって異なる場合があります）
                    # 一般的なXboxコントローラーのボタンマッピングを仮定しています。
                    # 必要に応じてボタン番号を調整してください。
                    if button == 4:  # L1
                        pwm_servo.setServoPwm(servo_channel_neck, 90)  # 下を向く
                        print("Servo が下を向きました。")
                    elif button == 5:  # R1
                        pwm_servo.setServoPwm(servo_channel_neck, 90)  # 上を向く
                        print("Servo が上を向きました。")
                    elif button == 6:  # L2
                        pwm_servo.setServoPwm(servo_channel_left_right, 90)  # 左を向く
                        print("Servo が左を向きました。")
                    elif button == 7:  # R2
                        pwm_servo.setServoPwm(servo_channel_left_right, 90)  # 右を向く
                        print("Servo が右を向きました。")

                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    print(f"ボタン {button} が離されました。")

                elif event.type == pygame.JOYHATMOTION:
                    hat = event.hat
                    value = event.value
                    print(f"ハット {hat} が動きました。値: {value}")

            # モーター制御用のジョイスティック入力を取得
            # 左スティック
            left_horizontal = joystick.get_axis(0)  # 左スティックのX軸
            left_vertical = joystick.get_axis(1)    # 左スティックのY軸

            # 右スティック
            right_horizontal = joystick.get_axis(3)  # 右スティックのX軸
            # right_vertical = joystick.get_axis(4)    # 右スティックのY軸（未使用）

            # 生の軸データを表示
            raw_axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
            print(f"Raw axes: {raw_axes}")

            # デッドゾーンの適用
            if abs(left_horizontal) < DEAD_ZONE_MOVEMENT:
                left_horizontal = 0
            if abs(left_vertical) < DEAD_ZONE_MOVEMENT:
                left_vertical = 0
            if abs(right_horizontal) < DEAD_ZONE_ROTATION:
                right_horizontal = 0
            # if abs(right_vertical) < DEAD_ZONE_ROTATION:
            #     right_vertical = 0

            # 移動方向の計算
            y = -left_vertical
            x = left_horizontal

            # 回転の計算
            rotation = right_horizontal  # 右スティックのX軸で回転を制御

            # 回転の強さを調整
            rotation_strength = rotation * 0.5  # 0.5倍

            # 各モーターへの指令値を計算
            front_left = y + x + rotation_strength
            front_right = y - x - rotation_strength
            back_left = y - x + rotation_strength
            back_right = y + x - rotation_strength

            # モーターの指令値を-1から1の範囲に正規化
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
            print(f"PWM values - FL: {duty_front_left}, FR: {duty_front_right}, BL: {duty_back_left}, BR: {duty_back_right}")

            # モーターに指令値を送信
            motor.setMotorModel(duty_front_left, duty_back_left, duty_front_right, duty_back_right)

            # サーボ制御用のジョイスティックボタンをチェック
            # 以下は例として、ボタンが押されたときにサーボを動かす方法です。
            # すでにJOYBUTTONDOWNイベントで処理しているため、必要に応じて追加処理を行ってください。

            # サーボ制御の他の方法が必要な場合は、ここに追加できます。

            # 待機時間
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
        # モーターを停止
        motor.setMotorModel(0, 0, 0, 0)
        # サーボを中立位置にリセット
        pwm_servo.setServoPwm(servo_channel_neck, 90)
        pwm_servo.setServoPwm(servo_channel_left_right, 90)
        sys.exit()

if __name__ == "__main__":
    print('プログラムを開始します...')
    if len(sys.argv) < 2:
        print("パラメータエラー: デバイスを指定してください")
        print("使用可能なデバイス: Led, Motor, Ultrasonic, Infrared, Servo, ADC, Buzzer, Rotate, Neck, Joystick")
        sys.exit()

    device = sys.argv[1]

    if device == 'Led':
        test_Led()
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
        main()
    else:
        print(f"不明なデバイス: {device}")
        print("使用可能なデバイス: Led, Motor, Ultrasonic, Infrared, Servo, ADC, Buzzer, Rotate, Neck, Joystick")
