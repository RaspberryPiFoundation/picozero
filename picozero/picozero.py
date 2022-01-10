from machine import Pin, PWM, Timer

class OutputDevice:
    
    def __init__(self, active_high=True, initial_value=False):
        self.active_high = active_high
        self._write(initial_value)
        self._timer = None
    
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
        
    def on(self):
        self._stop_blink()
        self.value = 1

    def off(self):
        self._stop_blink()
        self.value = 0
            
    @property
    def is_active(self):
        return bool(self.value)

    def toggle(self):
        if self.is_active:
            self.value = 0
        else:
            self.value = 1
            
    def blink(self, time=1):
        self._stop_blink()
        self._timer = Timer()
        self._timer.init(period=int(time * 1000), mode=Timer.PERIODIC, callback=self._blink_callback)
        
    def _blink_callback(self, timer_obj):
        self.toggle()

    def _stop_blink(self):
        if self._timer is not None:
            self._timer.deinit()
            self._timer = None

class DigitalOutputDevice(OutputDevice):
    """
    Represents a generic output device.

    :type pin: int
    :param pin:
        The pin that the device is connected to.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the GPIO
        to HIGH. If :data:`False`, the :meth:`on` method will set the GPIO to
        LOW (the :meth:`off` method always does the opposite).

    :type initial_value: bool
    :param initial_value:
        If :data:`False` (the default), the device will be off initially.  If
        :data:`None`, the device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on).  If
        :data:`True`, the device will be switched on initially.
    """
    def __init__(self, pin, active_high=True, initial_value=False):
        self._pin = Pin(pin, Pin.OUT)
        super().__init__(active_high, initial_value)
        
    def _value_to_state(self, value):
        return int(self._active_state if value else self._inactive_state)
    
    def _state_to_value(self, state):
        return int(bool(state) == self._active_state)
    
    def _read(self):
        return self._state_to_value(self._pin.value())

    def _write(self, value):
        self._pin.value(self._value_to_state(value))
        
class LED(DigitalOutputDevice):
    pass

LED.is_lit = LED.is_active

class Buzzer(DigitalOutputDevice):
    pass

Buzzer.beep = Buzzer.blink

class PWMOutputDevice(OutputDevice):
    def __init__(self, pin, freq=100, active_high=True, initial_value=False):
        self._pwm = PWM(Pin(pin))
        super().__init__(active_high, initial_value)
    
    def _state_to_value(self, state):
        return (state if self.active_high else 1 - state) / 65025

    def _value_to_state(self, value):
        return int(65025 * (value if self.active_high else 1 - value))
    
    def _read(self):
        return self._state_to_value(self._pwm.duty_u16())
    
    def _write(self, value):
        self._pwm.duty_u16(self._value_to_state(value))
        
    @property
    def is_active(self):
        return self.value != 0

class PWMLED(PWMOutputDevice):
    pass

PWMLED.is_list = PWMLED.is_active

class DigitalInputDevice:
    def __init__(self, pin, pull_up=False, active_state=None, bounce_time=0.2):
        self._pin = Pin(pin, mode=Pin.IN)
        self._pin.pull = Pin.PULL_UP if pull_up else Pin.PULL_DOWN
        self._pin.irq(self._pin_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        
    def _pin_change(self, p):
        pass
        
