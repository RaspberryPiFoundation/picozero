from picozero import Servo
from time import sleep

servo = Servo(1)

for i in range(0, 100):
    servo.value = i / 100
    sleep(0.1)

servo.off()
