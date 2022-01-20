from picozero import RGBLED, Pot
from time import sleep

rgb = RGBLED(red=2, green=1, blue=0)
dial = Pot(0)    
    
while True:
    hue = 255 - (dial.value * 255)
  
    if hue < 85:
        rgb.red = 255 - hue * 3
        rgb.green = 0
        rgb.blue = hue * 3

    elif hue < 170:
        hue -= 85;
        rgb.red = 0
        rgb.green = hue * 3
        rgb.blue = 255 - hue * 3
  
    else:
        hue -= 170;
        rgb.red = int(hue * 3)
        rgb.green = int(255 - (hue * 3))
        rgb.blue = 0
  
    #print(rgb.blue, hue, rgb.green, rgb.red) # order to match Thonny plotter colours
    print(hue, rgb.red, rgb.blue, rgb.green)
    sleep(0.1)
