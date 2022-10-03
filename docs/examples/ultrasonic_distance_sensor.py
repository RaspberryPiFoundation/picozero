from picozero import DistanceSensor
from time import sleep

ds = DistanceSensor(echo=2, trigger=3)

while True:
    print(ds.distance)
    sleep(0.1)
