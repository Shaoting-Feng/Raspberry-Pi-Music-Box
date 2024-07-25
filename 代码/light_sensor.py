import RPi.GPIO as GPIO
import os
GPIO.setmode(GPIO.BCM)
GPIO.setup(23,GPIO.IN)
cmd = "sudo halt"
GPIO.setwarnings(False)
while True:
    if GPIO.input(23):
        GPIO.cleanup()
        os.system(cmd)
