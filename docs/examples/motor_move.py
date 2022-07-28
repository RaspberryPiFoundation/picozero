from picozero import Motor
from time import sleep

motor = Motor(14, 15)

motor.move()
sleep(1)
motor.stop()