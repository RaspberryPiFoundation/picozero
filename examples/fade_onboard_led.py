from picozero import LED
from time import sleep

led = LED(25)

while True:
    for b in range(0, 100, 1):
        led.brightness = b/100
        sleep(0.02)
    for b in range(100, 0, -1):
        led.brightness = b/100
        sleep(0.02)
