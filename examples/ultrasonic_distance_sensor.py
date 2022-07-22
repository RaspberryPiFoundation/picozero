from picozero import DistanceSensor
from time import sleep

ds = DistanceSensor(5, 4)

while True:
    print(ds.distance)
    sleep(0.1)