# Blink the onboard LED, sleep for 10 seconds then stop the blinking

from time import sleep
from pico import Button, LED

led = LED()

led.blink(0.5)
print("Blinking")
sleep(10)
led.blink_stop()
print("Stopped blinking")
