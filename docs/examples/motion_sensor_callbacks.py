from picozero import MotionSensor, LED
from time import sleep

pir = MotionSensor(2)

# Create an LED on pin 25 (built-in LED)
led = LED(25)

# Set up event callbacks
pir.when_motion = led.on
pir.when_no_motion = led.off

# Keep the program running
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    led.off()  # Make sure LED is off when exiting
