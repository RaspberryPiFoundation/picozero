from picozero import RGBLED
from time import sleep

rgb = RGBLED(1, 2, 3)

rgb.pulse() # does not wait
sleep(6)
rgb.off()
sleep(1)

# 2 second to fade from purple to off, 0.5 seconds to change from off to purple 
rgb.pulse(fade_times=(2, 0.5), colors=((1, 0, 1), (0, 0, 0)), wait=True, n=3)

rgb.off()
sleep(1)

# 4 seconds to change from red to green, 2 to change from green to blue, then 1 to change from blue back to red
rgb.pulse((4, 2, 1), colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), wait=True, n=2)
