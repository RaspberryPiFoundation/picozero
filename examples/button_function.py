from picozero import Button, LED
from time import sleep

button = Button(17)
pico_led = LED(25) # pin 25 is the onboard led on the Pico

def led_on_off():
    pico_led.on()
    sleep(1)
    pico_led.off()
    
button.when_pressed = led_on_off
