from picozero import RGBLED
from time import sleep

rgb = RGBLED(1, 2, 3)

rgb.blink() # does not wait
sleep(6)
rgb.off()
sleep(1)

# blink purple 2 seconds, off 0.5 seconds
rgb.blink(on_times=(2, 0.5), colors=((255, 0, 255), (0, 0, 0)), wait=True, n=3)

rgb.off()
sleep(1)

# blink red 1 second, green 0.5 seconds, blue 0.25 seconds
rgb.blink((1, 0.5, 0.25), colors=((255, 0, 0), (0, 255, 0), (0, 0, 255)), wait=True, n=2)
    
