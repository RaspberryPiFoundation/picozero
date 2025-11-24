from picozero import Motor
from time import sleep

motor = Motor(14, 15)

motor.start()
sleep(1)
motor.stop()
