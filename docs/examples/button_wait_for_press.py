from picozero import Button

button = Button(18)

print("Press the button within 5 seconds")

if button.wait_for_press(timeout=5):
    print("Button was pressed")
else:
    print("Too slow!")
