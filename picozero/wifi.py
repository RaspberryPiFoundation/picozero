"""WiFi connectivity support for Raspberry Pi Pico W."""

from time import sleep

try:
    import network as _network_module
    
    class WiFi:
        """
        Provides WiFi connectivity for Raspberry Pi Pico W.
        
        :param int timeout:
            Default timeout in seconds for connection attempts. Defaults to 10.
        """
        
        def __init__(self, timeout=10):
            self._network = _network_module
            self._timeout = timeout
            self._sta = None
        
        def connect(self, ssid, password, timeout=None):
            """
            Connect to a WiFi network.
            
            :param str ssid:
                The network name (SSID) to connect to.
            
            :param str password:
                The network password.
            
            :param int timeout:
                Connection timeout in seconds. If None, uses the default timeout
                set during initialization. Defaults to None.
            
            :returns:
                The IP address assigned to the Pico W.
            
            :raises RuntimeError:
                If connection fails or times out.
            """
            if timeout is None:
                timeout = self._timeout
            
            self._sta = self._network.WLAN(self._network.STA_IF)
            
            if not self._sta.active():
                self._sta.active(True)
            
            if self._sta.isconnected():
                return self._sta.ifconfig()[0]
            
            self._sta.connect(ssid, password)
            
            # Wait for connection with timeout
            elapsed = 0
            while not self._sta.isconnected() and elapsed < timeout:
                sleep(0.2)
                elapsed += 0.2
            
            if not self._sta.isconnected():
                self._sta.active(False)
                raise RuntimeError(
                    f"Failed to connect to '{ssid}' - check SSID and password"
                )
            
            return self._sta.ifconfig()[0]
        
        def disconnect(self):
            """
            Disconnect from the WiFi network and deactivate the interface.
            """
            if self._sta is not None:
                self._sta.disconnect()
                self._sta.active(False)
                self._sta = None
        
        @property
        def is_connected(self):
            """
            Returns True if currently connected to a WiFi network.
            """
            return self._sta is not None and self._sta.isconnected()
        
        @property
        def ip(self):
            """
            Returns the current IP address, or None if not connected.
            """
            if self.is_connected:
                return self._sta.ifconfig()[0]
            return None
        
        @property
        def subnet(self):
            """
            Returns the subnet mask, or None if not connected.
            """
            if self.is_connected:
                return self._sta.ifconfig()[1]
            return None
        
        @property
        def gateway(self):
            """
            Returns the gateway address, or None if not connected.
            """
            if self.is_connected:
                return self._sta.ifconfig()[2]
            return None
        
        @property
        def dns(self):
            """
            Returns the DNS server address, or None if not connected.
            """
            if self.is_connected:
                return self._sta.ifconfig()[3]
            return None
        
        @property
        def signal_strength(self):
            """
            Returns the WiFi signal strength (RSSI) in dBm, or None if not connected.
            
            Typical values:
            - -30 dBm: Excellent signal
            - -50 dBm: Very good signal
            - -60 dBm: Good signal
            - -70 dBm: Fair signal
            - -80 dBm: Weak signal
            - -90 dBm: Very weak signal
            """
            if self.is_connected:
                return self._sta.status('rssi')
            return None
        
        @property
        def ssid(self):
            """
            Returns the SSID of the connected network, or None if not connected.
            """
            if self.is_connected:
                return self._sta.config('ssid')
            return None
        
        def info(self):
            """
            Returns a dictionary with connection information, or None if not connected.
            
            The dictionary includes:
            - ip: IP address
            - subnet: Subnet mask
            - gateway: Gateway address
            - dns: DNS server address
            - ssid: Network name
            - signal: Signal strength in dBm
            """
            if not self.is_connected:
                return None
            
            return {
                'ip': self.ip,
                'subnet': self.subnet,
                'gateway': self.gateway,
                'dns': self.dns,
                'ssid': self.ssid,
                'signal': self.signal_strength
            }

except ImportError:
    # WiFi not available on regular Pico
    pass
