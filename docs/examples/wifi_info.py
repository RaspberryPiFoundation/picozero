"""
Get detailed WiFi connection information
"""

from picozero import WiFi

wifi = WiFi()
wifi.connect("YourNetworkName", "YourPassword")

# Get all connection info
info = wifi.info()
print("Network:", info["ssid"])
print("IP:", info["ip"])
print("Subnet:", info["subnet"])
print("Gateway:", info["gateway"])
print("DNS:", info["dns"])
print("Signal:", info["signal"], "dBm")

# Check signal strength
signal = wifi.signal_strength
if signal > -50:
    print("Excellent signal!")
elif signal > -60:
    print("Good signal")
elif signal > -70:
    print("Fair signal")
else:
    print("Weak signal")
