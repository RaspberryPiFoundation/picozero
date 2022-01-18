from picozero import Button, LED

button = Button(17)
pico_led = LED(25) # pin 25 is the onboard led on the Pico

button.when_pressed = pico_led.on
button.when_released = pico_led.off
