from machine import Pin, PWM, ADC, Timer
from time import sleep, sleep_ms
from random import randint

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

class RGBLED():
    """
    TODO Add random colour selection from sensible range
    TODO Add cycle method which cycles through colour wheel of interesting colours
    TODO Add support for common cathode RGB LEDs
    """
    
    redLED = None
    greenLED = None
    blueLED = None
    blinkTimer = None
    
    def __init__(self, red_pin=2, green_pin=1, blue_pin=0):
        self.redLED = LED(red_pin)
        self.greenLED = LED(green_pin)
        self.blueLED = LED(blue_pin)
        
    def off(self):
        self.redLED.off()
        self.greenLED.off()
        self.blueLED.off()
        
    @property
    def red(self):
        return self.redLED.brightness
    
    @red.setter
    def red(self, value):
        self.redLED.brightness = value
        if self.redLED.brightness > 0:
            self.redLED.on()
        else:
            self.redLED.off()
            
    @property
    def green(self):
        return self.greenLED.brightness
    
    @green.setter
    def green(self, value):
        self.greenLED.brightness = value
        if self.greenLED.brightness > 0:
            self.greenLED.on()
        else:
            self.greenLED.off()
            
    @property
    def blue(self):
        return self.blueLED.brightness
    
    @blue.setter
    def blue(self, value):
        self.blueLED.brightness = value
        if self.blueLED.brightness > 0:
            self.blueLED.on()
        else:
            self.blueLED.off()
            
    @property
    def color(self):
        return (self.redLED.brightness, self.greenLED.brightness, self.blueLED.brightess)
    
    @blue.setter
    def color(self, value):
        self.redLED.brightness = value[0]
        self.greenLED.brightness = value[1]
        self.blueLED.brightness = value[2]
        
        if self.redLED.brightness > 0:
            self.redLED.on()
        else:
            self.redLED.off()
            
        if self.greenLED.brightness > 0:
            self.greenLED.on()
        else:
            self.greenLED.off()
            
        if self.blueLED.brightness > 0:
            self.blueLED.on()
        else:
            self.blueLED.off()

    def tick(self, timer):
        self.redLED.toggle()
        self.greenLED.toggle()
        self.blueLED.toggle()
        
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
        
    def random(self):
        self.red = randint(0, 100)
        self.green = randint(0, 100)
        self.blue = randint(0, 100)
        
ADCMAX = 65535
VOLTAGECONVERSION = 3.3 / ADCMAX

class Potentiometer(ADC):
    
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
        
class TemperatureSensor(ADC):
    
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

