from picozero import DistanceSensor
from time import sleep

ds = DistanceSensor(echo=5, trigger=4)

while True:
    print(ds.distance)
    sleep(0.1)