from picozero import RGBLED
from time import sleep

rgb = RGBLED(red=1, green=2, blue=3)

rgb.red = 255  # full red
sleep(1)
rgb.red = 128  # half red
sleep(1)

rgb.on()  # white

rgb.color = (0, 255, 0)  # full green
sleep(1)
rgb.color = (255, 0, 255)  # magenta
sleep(1)
rgb.color = (255, 255, 0)  # yellow
sleep(1)
rgb.color = (0, 255, 255)  # cyan
sleep(1)
rgb.color = (255, 255, 255)  # white
sleep(1)

rgb.color = (0, 0, 0)  # off
sleep(1)

# slowly increase intensity of blue
for n in range(255):
    rgb.blue = n
    sleep(0.01)
    
rgb.off()
