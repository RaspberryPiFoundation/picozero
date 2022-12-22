# Choose View -> Plotter in Thonny to see a graph of the results

from picozero import pico_temp_sensor
from time import sleep

while True:
    print(pico_temp_sensor.temp)
    sleep(0.1)
