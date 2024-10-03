import time
import sys
import pygame
from Motor import *
from Ultrasonic import *
from Line_Tracking import *
from servo import *
from ADC import *
from Buzzer import *

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

# メインプログラムのロジック:
if __name__ == '__main__':

    print ('Program is starting ... ')
    if len(sys.argv) < 2:
        print ("Parameter error: Please assign the device")
        exit() 

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
    else:
        print(f"Unknown device: {device}")
        print("Available devices: Led, Motor, Ultrasonic, Infrared, Servo, ADC, Buzzer, Rotate, Neck")
