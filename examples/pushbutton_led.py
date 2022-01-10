# Turn the onboard LED on when a push button is pressed and off when it is released

from time import sleep
from pico import Button, LED

button = Button(21)
led = LED()

button.when_pressed = led.on
button.when_released = led.off
