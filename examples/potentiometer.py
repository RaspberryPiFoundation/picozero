# Potentiometer connected to ADC0, GND and 3V

from time import sleep
from pico import Pot

pot = Pot(0)

while True:
    print(f"Reading: {pot.value}")
    print(f"Voltage: {pot.voltage}")
    print(f"Percent: {pot.percent}")
    sleep(0.1)
    
