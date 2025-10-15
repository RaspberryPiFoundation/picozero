from picozero import MotionSensor
from time import sleep

pir = MotionSensor(2)

print("PIR Motion Sensor Example")
print("Waiting for motion...")

while True:
    if pir.motion_detected:
        print("Motion detected!")
        sleep(1)
    else:
        print("No motion")
        sleep(0.5)
