import pygame
import time
import os
import sys

class Buzzer:
    def __init__(self, sound_file='/home/ogawamasaki/car_project/ Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server-pi5/data/maou_se_system49.wav', volume=0.7):
        # Prevent running as sudo
        if os.geteuid() == 0:
            print("??????????????sudo?????????????")
            sys.exit(1)

        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            print("pygame.mixer????????????")
        except pygame.error as e:
            print(f"pygame.mixer???????????: {e}")
            sys.exit(1)

        # Check if sound file exists
        if not os.path.exists(sound_file):
            print(f"??????????????: {sound_file}")
            sys.exit(1)
        else:
            print(f"?????????????: {sound_file}")

        # Load sound file
        try:
            self.sound = pygame.mixer.Sound(sound_file)
            self.sound.set_volume(volume)
            print("??????????????????")
        except pygame.error as e:
            print(f"?????????????????: {e}")
            sys.exit(1)

    def run(self, command):
        if command != "0":
            print("Buzzer ON: ?????????")
            self.sound.play()
        else:
            print("Buzzer OFF: ????????????")
            self.sound.stop()

if __name__ == '__main__':
    buzzer = Buzzer()
    buzzer.run('1')
    time.sleep(3)
    buzzer.run('0')
    print("End of program")
