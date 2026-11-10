from picozero import Button, pico_led, pause

button = Button(18, hold_time=2)

button.when_held = pico_led.on
button.when_released = pico_led.off

pause()
