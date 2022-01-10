# Print the temperature from the onboard temperature sensor in degrees C
# Choose View -> Plotter in Thonny to see a graph of the results

from time import sleep
from pico import TempSensor

picoTemp = TempSensor()

while True:
    print(f"Temperature: {picoTemp.temp} degrees C")
    sleep(0.1)
