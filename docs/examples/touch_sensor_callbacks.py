from picozero import TouchSensor, pico_led
from time import sleep

touch = TouchSensor(2)

# Set up event callbacks
touch.when_touched = pico_led.on
touch.when_touch_ends = pico_led.off

# Keep the program running
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    pico_led.off()  # Make sure LED is off when exiting
