from picozero import TouchSensor, pico_led
from time import sleep

# Capacitive touch sensor output connected to pin 2
touch = TouchSensor(2)

while True:
    if touch.is_touched:
        pico_led.on()
    else:
        pico_led.off()
    sleep(0.1)
