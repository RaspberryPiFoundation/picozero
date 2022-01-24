# Choose View -> Plotter in Thonny to see a graph of the results

from time import sleep
from picozero import pico_temp_sensor

while True:
    print(pico_temp_sensor.temp)
    sleep(0.1)
