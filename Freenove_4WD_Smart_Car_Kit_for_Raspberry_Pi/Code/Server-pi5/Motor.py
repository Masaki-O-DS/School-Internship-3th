# Motor.py
import time
import math
from PCA9685 import PCA9685
from ADC import *

class Motor:
    def __init__(self):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(1000)
        self.time_proportion = 3  # 使用されていないようです
        self.adc = Adc()
        self.left_motor_scaling = 0.7  # 左側モーターのスケーリングファクターを0.7に変更
        self.MIN_DUTY = 100  # モーターが動作する最低限のデューティサイクル
    
    def duty_range(self, duty1, duty2, duty3, duty4):
        duty1 = max(min(duty1, 4095), -4095)
        duty2 = max(min(duty2, 4095), -4095)
        duty3 = max(min(duty3, 4095), -4095)
        duty4 = max(min(duty4, 4095), -4095)
        return duty1, duty2, duty3, duty4
    
    def left_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(0, 0)
            self.pwm.setMotorPwm(1, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(1, 0)
            self.pwm.setMotorPwm(0, abs(duty))
        else:
            self.pwm.setMotorPwm(0, 0)
            self.pwm.setMotorPwm(1, 0)
    
    def left_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(3, 0)
            self.pwm.setMotorPwm(2, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(2, 0)
            self.pwm.setMotorPwm(3, abs(duty))
        else:
            self.pwm.setMotorPwm(2, 0)
            self.pwm.setMotorPwm(3, 0)
    
    def right_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(6, 0)
            self.pwm.setMotorPwm(7, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(7, 0)
            self.pwm.setMotorPwm(6, abs(duty))
        else:
            self.pwm.setMotorPwm(6, 0)
            self.pwm.setMotorPwm(7, 0)
    
    def right_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(4, 0)
            self.pwm.setMotorPwm(5, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(5, 0)
            self.pwm.setMotorPwm(4, abs(duty))
        else:
            self.pwm.setMotorPwm(4, 0)
            self.pwm.setMotorPwm(5, 0)
    
    def setMotorModel(self, duty1, duty2, duty3, duty4, turning=False):
        duty1, duty2, duty3, duty4 = self.duty_range(duty1, duty2, duty3, duty4)
        if turning:
            scaling = 1.2  # 旋回時のスケーリング
        else:
            scaling = 0.8  # 直進時のスケーリング
        # 左側のモーターのデューティ比を調整
        duty1 = int(duty1 * self.left_motor_scaling * scaling)
        duty2 = int(duty2 * self.left_motor_scaling * scaling)
        
        # 最低出力閾値の適用
        duty1 = duty1 if abs(duty1) > self.MIN_DUTY else 0
        duty2 = duty2 if abs(duty2) > self.MIN_DUTY else 0
        
        self.left_Upper_Wheel(duty1)
        self.left_Lower_Wheel(duty2)
        self.right_Upper_Wheel(duty3)
        self.right_Lower_Wheel(duty4)
    
    def Rotate(self, direction, speed=2000):
        """
        direction: 'left' または 'right'
        speed: 0～4095の範囲
        """
        if direction == 'right':
            # 右回転
            self.setMotorModel(speed, speed, -speed, -speed)
        elif direction == 'left':
            # 左回転
            self.setMotorModel(-speed, -speed, speed, speed)
        else:
            # 停止
            self.setMotorModel(0, 0, 0, 0)
    
    def stop(self):
        self.setMotorModel(0, 0, 0, 0)
