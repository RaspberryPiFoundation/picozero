from picozero import Stepper
from time import localtime, sleep

# The Pico doesn't keep the time when it is unplugged. Thonny sets the clock
# when it connects, and a Pico W can set it from the internet using ntptime.

stepper = Stepper((1, 2, 3, 4), step_sequence="half")

OPEN_TIME = (7, 0)  # Open at 7:00 AM (hour, minute)
CLOSE_TIME = (20, 0)  # Close at 8:00 PM
ROTATIONS = 5  # Number of full rotations needed to fully open/close blinds

# Track state
is_open = False


def open_blinds():
    global is_open
    if not is_open:
        for _ in range(ROTATIONS):
            stepper.rotate(1, "cw")
        stepper.off()  # don't keep the coils powered until the next move
        is_open = True


def close_blinds():
    global is_open
    if is_open:
        for _ in range(ROTATIONS):
            stepper.rotate(1, "ccw")
        stepper.off()  # don't keep the coils powered until the next move
        is_open = False


def check_schedule():
    # MicroPython's localtime() returns a tuple:
    # (year, month, day, hour, minute, second, weekday, yearday)
    now = localtime()
    current_time = (now[3], now[4])

    # Check if it's time to open
    if current_time == OPEN_TIME and not is_open:
        open_blinds()

    # Check if it's time to close
    elif current_time == CLOSE_TIME and is_open:
        close_blinds()


# Set starting position (closed)
stepper.reset_position()
is_open = False

# Check every 30 seconds
while True:
    check_schedule()
    sleep(30)
