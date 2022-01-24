from picozero import Button, pico_led
from time import sleep

button = Button(17)

def led_on_off():
    pico_led.on()
    sleep(1)
    pico_led.off()
    
button.when_pressed = led_on_off
