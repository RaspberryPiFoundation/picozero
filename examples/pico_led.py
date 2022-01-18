from picozero import LED
from time import sleep

pico_led = LED(25) # pin 25 is the onboard led on the Pico

pico_led.on()
sleep(1)
pico_led.off()
