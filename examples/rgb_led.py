# Common cathode LED connected to GND and red = 2, green = 1, blue - 0
from time import sleep
from pico import RGBLED

rgb = RGBLED()

print("Red")
rgb.color = (100, 0, 0)

sleep(2)

print("Green")
rgb.color = (0, 100, 0)

sleep(2)

print("Blue")
rgb.color = (0, 0, 100)

sleep(2)

print("Pink")
rgb.color = (100, 0, 50)

sleep(2)

print("Disco")

while True:
    rgb.random()
    sleep(1)

