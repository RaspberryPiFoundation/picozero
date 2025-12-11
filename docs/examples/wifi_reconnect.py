"""
How to handle WiFi reconnection in a long-running program

For programs that run continuously, you may want to check the connection
periodically and reconnect if it's been lost.
"""

from picozero import WiFi
from time import sleep

wifi = WiFi()
wifi.connect("YourNetworkName", "YourPassword")

while True:
    # Check if still connected
    if not wifi.is_connected:
        print("Connection lost! Reconnecting...")
        try:
            wifi.connect("YourNetworkName", "YourPassword")
            print("Reconnected! IP:", wifi.ip)
        except RuntimeError as e:
            print("Reconnection failed:", e)
            print("Will retry in 60 seconds...")

    # Do your work here
    print("Signal strength:", wifi.signal_strength, "dBm")

    # Check again in 60 seconds
    sleep(60)
