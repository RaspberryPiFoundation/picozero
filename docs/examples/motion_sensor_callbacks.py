from picozero import MotionSensor, LED
from time import sleep

pir = MotionSensor(2)
led = LED(14)

print("Advanced PIR Motion Sensor Example")
print("Using event callbacks for motion detection...")


def motion_detected():
    print("🚶 Motion detected!")
    led.on()  # Turn on LED when motion detected


def no_motion():
    print("😴 No motion detected")
    led.off()  # Turn off LED when no motion


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
