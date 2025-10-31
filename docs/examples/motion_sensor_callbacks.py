from picozero import MotionSensor, pico_led
from time import sleep

pir = MotionSensor(2)

# Set up event callbacks
pir.when_motion = pico_led.on
pir.when_no_motion = pico_led.off

# Keep the program running
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    pico_led.off()  # Make sure LED is off when exiting
