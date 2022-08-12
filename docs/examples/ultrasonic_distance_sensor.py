from picozero import DistanceSensor
from time import sleep

ds = DistanceSensor(echo=4, trigger=5)

while True:
    print(ds.distance)
    sleep(0.1)
