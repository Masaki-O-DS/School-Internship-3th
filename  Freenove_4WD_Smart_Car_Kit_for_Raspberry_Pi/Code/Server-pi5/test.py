import time

        
        
from Motor import *            
PWM=Motor()          
def test_Motor(): 
    try:
        PWM.setMotorModel(1000,1000,1000,1000)         #Forward
        print ("The car is moving forward")
        time.sleep(1)
        PWM.setMotorModel(-1000,-1000,-1000,-1000)     #Back
        print ("The car is going backwards")
        time.sleep(1)
        PWM.setMotorModel(-1500,-1500,2000,2000)       #Turn left
        print ("The car is turning left")
        time.sleep(1)
        PWM.setMotorModel(2000,2000,-1500,-1500)       #Turn right 
        print ("The car is turning right")  
        time.sleep(1)
        PWM.setMotorModel(-2000,2000,2000,-2000)       #Move left 
        print ("The car is moving left")  
        time.sleep(1)
        PWM.setMotorModel(2000,-2000,-2000,2000)       #Move right 
        print ("The car is moving right")  
        time.sleep(1)    
            
        PWM.setMotorModel(0,2000,2000,0)         #Move diagonally to the left and forward
        print ("The car is moving diagonally to the left and forward")  
        time.sleep(1)
        PWM.setMotorModel(0,-2000,-2000,0)       #Move diagonally to the right and backward
        print ("The car is moving diagonally to the right and backward")  
        time.sleep(1) 
        PWM.setMotorModel(2000,0,0,2000)         #Move diagonally to the right and forward
        print ("The car is moving diagonally to the right and forward")  
        time.sleep(1)
        PWM.setMotorModel(-2000,0,0,-2000)       #Move diagonally to the left and backward
        print ("The car is moving diagonally to the left and backward")  
        time.sleep(1) 
        
        PWM.setMotorModel(0,0,0,0)               #Stop
        print ("\nEnd of program")
    except KeyboardInterrupt:
        PWM.setMotorModel(0,0,0,0)
        print ("\nEnd of program")


from Ultrasonic import *
ultrasonic=Ultrasonic()                
def test_Ultrasonic():
    try:
        while True:
            data=ultrasonic.get_distance()   #Get the value
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

from Line_Tracking import *
line=Line_Tracking()
def test_Infrared():
    try:
        line.test_Infrared()
    except KeyboardInterrupt:
        print ("\nEnd of program")


from servo import *
pwm=Servo()
def test_Servo():
    try:
        while True:
            for i in range(50, 110, 1):
                pwm.setServoPwm('0', i)
                print(f"Servo 0 set to {i} degrees")
                time.sleep(0.01)
            for i in range(110, 50, -1):
                pwm.setServoPwm('0', i)
                print(f"Servo 0 set to {i} degrees")
                time.sleep(0.01)
            for i in range(80, 150, 1):
                pwm.setServoPwm('1', i)
                print(f"Servo 1 set to {i} degrees")
                time.sleep(0.01)
            for i in range(150, 80, -1):
                pwm.setServoPwm('1', i)
                print(f"Servo 1 set to {i} degrees")
                time.sleep(0.01)   
    except KeyboardInterrupt:
        pwm.setServoPwm('0', 90)
        pwm.setServoPwm('1', 90)
        print ("\nEnd of program")

        
        
from ADC import *
adc=Adc()
def test_Adc():
    try:
        while True:
            Left_IDR=adc.recvADC(0)
            print ("The photoresistor voltage on the left is "+str(Left_IDR)+"V")
            Right_IDR=adc.recvADC(1)
            print ("The photoresistor voltage on the right is "+str(Right_IDR)+"V")
            Power=adc.recvADC(2)
            print ("The battery voltage is "+str(Power*3)+"V")
            time.sleep(1)
            print ('\n')
    except KeyboardInterrupt:
        print ("\nEnd of program")

from Buzzer import *
buzzer=Buzzer()
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
           
# Main program logic follows:
if __name__ == '__main__':

    print ('Program is starting ... ')
    import sys
    if len(sys.argv)<2:
        print ("Parameter error: Please assign the device")
        exit() 
    if sys.argv[1] == 'Led':
        test_Led()
    elif sys.argv[1] == 'Motor':
        test_Motor()
    elif sys.argv[1] == 'Ultrasonic':
        test_Ultrasonic()
    elif sys.argv[1] == 'Infrared':
        test_Infrared()        
    elif sys.argv[1] == 'Servo': 
        test_Servo()               
    elif sys.argv[1] == 'ADC':   
        test_Adc()  
    elif sys.argv[1] == 'Buzzer':   
        test_Buzzer()  
    elif sys.argv[1] == 'Rotate':
        car_Rotate()
        
        
        
        
