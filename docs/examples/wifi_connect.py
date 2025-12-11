"""
Simple WiFi connection example for Raspberry Pi Pico W
"""

from picozero import WiFi

wifi = WiFi()
wifi.connect("YourNetworkName", "YourPassword")
