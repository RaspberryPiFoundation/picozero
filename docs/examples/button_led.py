from picozero import Button, pico_led

button = Button(17)

button.when_pressed = pico_led.on
button.when_released = pico_led.off
