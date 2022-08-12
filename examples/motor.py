from picozero import Motor
from time import sleep

m = Motor(12, 13)

# turn the motor for 1 second
print("the motor is turning")
m.move()
sleep(1)
m.stop()

# or alternatively turn it at half speed for 2 seconds
m.move(speed=0.5, t=2)
print("the motor will turn at half speed and stop after 2 seconds")