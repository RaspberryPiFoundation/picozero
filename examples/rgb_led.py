# Common anode LED connected to GND and red = 2, green = 1, blue - 0
from time import sleep
from picozero import RGBLED

rgb = RGBLED(2, 1, 0)

print("Red")
rgb.color = (1, 0, 0)

sleep(2)

print("Green")
rgb.color = (0, 1, 0)

sleep(2)

print("Blue")
rgb.color = (0, 0, 1)

sleep(2)

print("Pink")
rgb.color = (1, 0, 0.5)

sleep(2)

print("Blink")
rgb.blink()




