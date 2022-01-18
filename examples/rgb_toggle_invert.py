from picozero import RGBLED
from time import sleep

rgb = RGBLED(red=2, green=1, blue=0)

rgb.color = (255, 165, 0) # yellow
sleep(1)

for _ in range(6):
    rgb.toggle()
    sleep(1)

for _ in range(6):
    rgb.invert()
    sleep(1)
    
rgb.off()
