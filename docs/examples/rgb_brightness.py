from picozero import RGBLED
from time import sleep

rgb = RGBLED(red=1, green=2, blue=3)

# start with a mixed colour so brightness changes are obvious
rgb.color = (255, 128, 0)  # orange

while True:
    rgb.brightness = 0.2  # dim
    sleep(1)
    rgb.brightness = 0.6  # medium
    sleep(1)
    rgb.brightness = 1.0  # full
    sleep(1)
