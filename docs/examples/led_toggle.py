from picozero import LED
from time import sleep

led = LED(14)

while True:
    led.toggle()
    sleep(1)

