from picozero import TouchSensor
from time import sleep

touch = TouchSensor(2)

print("Touch the sensor...")

while True:
    if touch.is_touched:
        print("Touch detected!")
    else:
        print("No touch")
    sleep(0.1)
