from picozero import Button
from time import sleep

button = Button(18)

while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print("Button is not pressed")
    sleep(0.1)
