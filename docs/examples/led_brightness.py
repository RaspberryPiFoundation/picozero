from picozero import LED
from time import sleep

led = LED(14)

while True:
    led.brightness = 0  # off
    sleep(1)
    led.brightness = 0.5  # half brightness
    sleep(1)
    led.brightness = 1  # full brightness
    sleep(1)
