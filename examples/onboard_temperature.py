# Print the temperature from the onboard temperature sensor in degrees C
# Choose View -> Plotter in Thonny to see a graph of the results

from time import sleep
from picozero import onboard_temp_sensor

while True:
    print(onboard_temp_sensor.temp)
    sleep(0.1)
