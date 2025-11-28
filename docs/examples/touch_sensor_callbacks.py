from picozero import TouchSensor, pico_led
from time import sleep

touch = TouchSensor(2)

touch.when_touch_starts = pico_led.on
touch.when_touch_ends = pico_led.off
