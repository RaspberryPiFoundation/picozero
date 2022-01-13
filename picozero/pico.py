from machine import Pin, PWM, ADC, Timer
from time import sleep, sleep_ms
from random import randint
from picozero import OutputDevice

class RGBLED(DigitalOutputDevice):
    def __init__(self, red=None, green=None, blue=None, active_high=True,
                 initial_value=(0, 0, 0), pwm=True):
        super().__init__(active_high, initial_value)
        self._leds = ()
        #if not all(p is not None for p in [red, green, blue]):
        #    raise GPIOPinMissing('red, green, and blue pins must be provided')
        LEDClass = PWMLED if pwm else LED
        self._leds = tuple(
            LEDClass(pin, active_high=active_high)
            for pin in (red, green, blue))
        self.value = initial_value
        
    def close(self):
        if getattr(self, '_leds', None):
            self._stop_blink()
            for led in self._leds:
                led.close()
        self._leds = ()
        super().close()

    @property
    def closed(self):
        return len(self._leds) == 0

    @property
    def value(self):
        """
        Represents the color of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 1 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 1 if not).
        For example, red would be ``(1, 0, 0)`` and yellow would be ``(1, 1,
        0)``, while orange would be ``(1, 0.5, 0)``.
        """
        return tuple(led.value for led in self._leds)

    @value.setter
    def value(self, value):
        for component in value:
            if not 0 <= component <= 1:
                raise OutputDeviceBadValue(
                    'each RGB color component must be between 0 and 1')
            if isinstance(self._leds[0], LED):
                if component not in (0, 1):
                    raise OutputDeviceBadValue(
                        'each RGB color component must be 0 or 1 with non-PWM '
                        'RGBLEDs')
        for led, v in zip(self._leds, value):
            led.value = v

    @property
    def is_active(self):
        """
        Returns :data:`True` if the LED is currently active (not black) and
        :data:`False` otherwise.
        """
        return self.value != (0, 0, 0)

    is_lit = is_active

    @property
    def color(self):
        """
        Represents the color of the LED as a tuple.
        """
        return self.value

    @color.setter
    def color(self, value):
        self.value = value

    @property
    def red(self):
        """
        Represents the red element of the LED.
        """
        return self.value[0]

    @red.setter
    def red(self, value):
        r, g, b = self.value
        self.value = value, g, b

    @property
    def green(self):
        """
        Represents the green element of the LED.
        """
        return self.value[1]

    @green.setter
    def green(self, value):
        r, g, b = self.value
        self.value = r, value, b

    @property
    def blue(self):
        """
        Represents the blue element of the LED.
        """
        return self.value[2]

    @blue.setter
    def blue(self, value):
        r, g, b = self.value
        self.value = r, g, value

    def on(self):
        """
        Turn the LED on. This equivalent to setting the LED color to white
        ``(1, 1, 1)``.
        """
        self.value = (1, 1, 1)

    def off(self):
        """
        Turn the LED off. This is equivalent to setting the LED color to black
        ``(0, 0, 0)``.
        """
        self.value = (0, 0, 0)

    def toggle(self):
        """
        Toggle the state of the device. If the device is currently off
        (:attr:`value` is ``(0, 0, 0)``), this changes it to "fully" on
        (:attr:`value` is ``(1, 1, 1)``).  If the device has a specific color,
        this method inverts the color.
        """
        r, g, b = self.value
        self.value = (1 - r, 1 - g, 1 - b)
        
class AnalogInputDevice():
    def __init__(self, pin, active_high=True, threshold=0.5):
        self._adc = ADC(pin)
        self.active_high = active_high
        self.threshold = float(threshold)
    
    @property
    def active_high(self):
        return self._active_state

    @active_high.setter
    def active_high(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True
        
    @property
    def value(self):
        return self._read()

    @value.setter
    def value(self, value):
        self._write(value)
        
    def _state_to_value(self, state):
        return (state if self.active_high else 1 - state) / 65535

    def _value_to_state(self, value):
        return int(65535 * (value if self.active_high else 1 - value))
    
    def _read(self):
        return self._state_to_value(self._adc.read_u16())
        
    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = float(value)

    @property
    def is_active(self):
        return self.value > self.threshold

    @property
    def voltage(self):
        return self.value * 3.3
    
    @property
    def percent(self):
        return int(self.value * 100)
    
class Potentiometer(AnalogInputDevice):
    pass

Pot = Potentiometer

def onboard_temp_conversion(voltage):
    # Formula for calculating temp from voltage for the onboard temperature sensor
    return 27 - (voltage - 0.706)/0.001721

class TemperatureSensor(AnalogInputDevice):
    def __init__(self, pin, active_high=True, threshold=0.5, conversion=None):
         self._conversion = conversion
         super().__init__(pin, active_high, threshold)
        
    @property
    def temp(self):
        if self._conversion is not None:
            return self._conversion(self.voltage)
        else:
            return None
       
onboard_temp_sensor = TemperatureSensor(4, True, 0.5, onboard_temp_conversion)
TempSensor = TemperatureSensor
Thermistor = TemperatureSensor

# Old stuff below here

onboardLEDPin = 25
tempSensorADCPin = 4
ADCPins = [26, 27, 28]

"""
TODO Decide on whether to use 100/255/1.0 or other number for ranges and make consistent
TODO Decide how to do debug output (do we have a logging library, is that too big a dependency?)
"""

def info(message):
    print(message)
    
from machine import Pin, PWM

class Info():
    _info = True

class LED(PWM, Info):
    
    """
    TODO Is there a reason for this max instead of 65535 (it's in our guide)
    TODO Could support fade (although easy to do)
    """
    
    DUTYMAX = 65025
    blinkTimer = None

    def __init__(self, pin=25, brightness=100, with_info=True):
        
        self._info = with_info
        
        # brightness as a property of an LED
        self._brightness = brightness
        super().__init__(Pin(pin))
        # turn it off at start
        self.off()
        
        if self._info:
            if pin == 25:
                info("Onboard LED (pin 25)")
            else:
                info(f"LED with positive (long) leg in pin {pin} and negative (short/flat side) leg connected to GND")
            
    def on(self):
        self.duty_u16(int(self._brightness / 100 * self.DUTYMAX))
        
    def off(self):
        self.duty_u16(0)
        
    def toggle(self):
        if self.value == 0:
            self.on()
        else:
            self.off()
            
    def tick(self, timer):
        self.toggle()
        
    def blink(self, delay=1):
        
        if self.blinkTimer is not None:
            self.blinkTimer.deinit()
        else:
            self.blinkTimer = Timer()
            
        self.blinkTimer.init(freq=1/delay, mode=Timer.PERIODIC, callback=self.tick)
                        
    def blink_stop(self):
        if self.blinkTimer is not None:
            self.blinkTimer.deinit()
        self.off()
        
    @property
    def brightness(self):
        return self._brightness
    
    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        if self._brightness > 0:
            self.on()
        else:
            self.off()
    
    @property
    def value(self):
        return int(self.duty_u16() != 0)
    
    @value.setter
    def value(self, value):
        if value == 1:
            self.on()
        else:
            self.off() 
            
class Button(Pin, Info):
    """
    TODO Add callbacks for when_pressed, when_released
    TODO Debounce
    TODO Other options such as held as supported by gpio zero
    """
    
    GND = True # True - Connected to GND Pin; False - Connected to 3V Pin
    UNKNOWN = 0
    CLOSED = 1
    OPEN = 2
    
    def __init__(self, pin, GND=True, with_info=True, events=True):
        self.GND = True
        self.pin_number = pin
                      
        if GND:
            super().__init__(pin, Pin.IN, Pin.PULL_UP)
        else:
            super().__init__(pin, Pin.IN, Pin.PULL_DOWN)
                       
        self.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handle_interrupt)
                   
        if self._info:
            if GND == True:
                info(f"Button connected to GND and pin {pin}")
            else:
                info(f"Button connected to pin {pin} and 3V")
                
    pin_number = None
    _last_state = UNKNOWN
        
    @property
    def is_open(self):
        return not self.is_pressed
    
    @property
    def is_pressed(self):
        return not self.value() if self.GND else self.value()
    
    def _handle_interrupt(self, flags):        
        if self.is_pressed:
            self._when_pressed()
        else:
            self._when_released()
                         
    def _when_pressed(self):
        if self._last_state != self.CLOSED:
            info(f"Button {self.pin_number} pressed")
            self.when_pressed()       
        self._last_state = self.CLOSED
        
    def _when_released(self):
        if self._last_state != self.OPEN:
            info(f"Button {self.pin_number} released")
            self.when_released()
        self._last_state = self.OPEN
        
    def when_pressed(self): pass
    def when_released(self): pass
    
Switch = Button
Button.is_closed = Button.is_pressed
Button.is_latched = Button.is_closed
Button.is_on = Button.is_pressed
Button.is_off = Button.is_open

class Speaker(PWM):
    
    """
    TODO Add support for midi and abc notation - e.g. as for TonalBuzzer in gpio zero
    """
    
    VOLUMEMAX = 1023
    
    def __init__(self, pin=14, volume=100):    
        super().__init__(Pin(pin))
        self._volume = volume
        # turn it off at start
        self.stop()
        
    def play(self, freq=440, duration=1):
        self.duty_u16(int(self.volume / 100 * self.VOLUMEMAX))
        self.freq(freq)
        sleep(duration)
        self.duty_u16(0)       
        
    def stop(self):
        self.duty_u16(0)
        
    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value):
        self._volume = value
        self.duty_u16(value / 100 * self.VOLUMEMAX)
        
ADCMAX = 65535
VOLTAGECONVERSION = 3.3 / ADCMAX

class PotentiometerOld(ADC):
    
    """
    TODO allow setting of observable min and max range (pots often don't get down to zero)
    TODO should value always be a percent (or 255 or whatever we decide on) or should that be another option?
    """
    
    def __init__(self, adc=0):    
        super().__init__(adc)
        
    @property
    def value(self):
        return self.read_u16()
    
    @property
    def voltage(self):
        return self.value * VOLTAGECONVERSION
    
    @property
    def percent(self):
        return int(self.value / ADCMAX * 100)
    
Pot = Potentiometer
        
class TemperatureSensorOld(ADC):
    
    def __init__(self, adc=4, with_info=True):
        super().__init__(adc)
        self.adc_number = adc
    
    adc_number = None
        
    @property
    def value(self):
        return self.read_u16()
    
    @property
    def voltage(self):
        return self.value * VOLTAGECONVERSION
    
    @property
    def temp(self):
        # Formula for calculating temp from voltage
        return 27 - (self.voltage - 0.706)/0.001721
    
    
TempSensor = TemperatureSensor
Thermistor = TemperatureSensor
    
class PressureSensor():
    """
    TODO Add Velostat pressure sensor
    """
    pass

class VibrationMotor():
    """
    TODO Add vibration motor
    """
    pass

