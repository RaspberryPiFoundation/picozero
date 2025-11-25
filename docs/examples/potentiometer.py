# Potentiometer connected to GP26 (ADC0), GND and 3V

from time import sleep
from picozero import Pot

pot = Pot(26)

while True:
    print(pot.value, pot.voltage)
    sleep(0.1)
    
