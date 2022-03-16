from picozero import RGBLED
from time import sleep

rgb = RGBLED(1, 2, 3)

# Gradually colour cycle through colours between red and green, green and blue then blue and red
rgb.cycle()
sleep(4)
rgb.off()
sleep(1)

# Colour cycle slower in the opposite direction
rgb.cycle(fade_times=3, colors=((0, 0, 1), (0, 1, 0), (1, 0, 0)), wait=True, n=2)
rgb.off()
