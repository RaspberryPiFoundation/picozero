from picozero import MotionSensor, LED
from time import sleep

pir = MotionSensor(2)

# Create an LED on pin 25 (built-in LED)
led = LED(25)


def motion_detected():
    led.on()


def no_motion():
    led.off()


# Set up event callbacks
pir.when_motion = motion_detected
pir.when_no_motion = no_motion

# Keep the program running
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    led.off()  # Make sure LED is off when exiting
