from machine import Pin, PWM, Timer
from time import ticks_ms

class PWMChannelAlreadyInUse(Exception):
    pass

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
            self.off()
        else:
            self.on()
            
    def blink(self, time=1):
        self._stop_blink()
        self._timer = Timer()
        self._timer.init(period=int(time * 1000), mode=Timer.PERIODIC, callback=self._blink_callback)
        
    def _blink_callback(self, timer_obj):
        if self.is_active:
            self.value = 0
        else:
            self.value = 1

    def _stop_blink(self):
        if self._timer is not None:
            self._timer.deinit()
            self._timer = None
            
    def __del__(self):
        self._stop_blink()

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
        
class DigitalLED(DigitalOutputDevice):
    pass

DigitalLED.is_lit = DigitalLED.is_active

class Buzzer(DigitalOutputDevice):
    pass

Buzzer.beep = Buzzer.blink

class PWMOutputDevice(OutputDevice):
    
    PIN_TO_PWM_CHANNEL = ["0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B","7A","7B","0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B"]
    _channels_used = {}
    
    def __init__(self, pin, freq=100, active_high=True, initial_value=False):
        self._check_pwm_channel(pin)
        self._pin_num = pin
        self._pwm = PWM(Pin(pin))
        super().__init__(active_high, initial_value)
        
    def _check_pwm_channel(self, pin_num):
        channel = PWMOutputDevice.PIN_TO_PWM_CHANNEL[pin_num]
        if channel in PWMOutputDevice._channels_used.keys():
            raise PWMChannelAlreadyInUse(
                f"PWM channel {channel} is already in use by pin {PWMOutputDevice._channels_used[channel]}"
                )
        else:
            PWMOutputDevice._channels_used[channel] = pin_num
    
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
    
    def __del__(self):
        PWMOutputDevice._channels_used.remove(
            PWMOutputDevice.PIN_TO_PWM_CHANNEL[self._pin_num]
            )
    
class PWMLED(PWMOutputDevice):
    def __init__(self, pin, active_high=True, initial_value=False):
        self._brightness = 1
        super().__init__(pin=pin,
            active_high=active_high,
            initial_value=initial_value)
        
    @property
    def brightness(self):
        return self._brightness
    
    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        self.value = 1 if self._brightness > 0 else 0
                
    def _write(self, value):
        super()._write(self._brightness * value)
    
    def _read(self):
        return 1 if super()._read() > 0 else 0
    
# factory for returning an LED
def LED(pin, use_pwm=True, active_high=True, initial_value=False):
    if use_pwm:
        return PWMLED(
            pin=pin,
            active_high=active_high,
            initial_value=initial_value)
    else:
        return DigitalLED(
            pin=pin,
            active_high=active_high,
            initial_value=initial_value)

class DigitalInputDevice:
    def __init__(self, pin, pull_up=False, active_state=None, bounce_time=None):
        self._pin = Pin(
            pin,
            mode=Pin.IN,
            pull=Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self._bounce_time = bounce_time
        
        if active_state is None:
            self._active_state = False if pull_up else True
        else:
            self._active_state = active_state
        
        self._value = self._state_to_value(self._pin.value())
        
        self._when_activated = None
        self._when_deactivated = None
        
        # setup interupt
        self._pin.irq(self._pin_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        
    def _state_to_value(self, state):
        return int(bool(state) == self._active_state)
        
    def _pin_change(self, p):
        # turn off the interupt
        p.irq(handler=None)
        
        last_state = p.value()
        
        if self._bounce_time is not None:
            # wait for stability
            stop = ticks_ms() + (self._bounce_time * 1000)
            while ticks_ms() < stop:
                # keep checking, reset the stop if the value changes
                if p.value() != last_state:
                    stop = ticks_ms() + self._bounce_time
                    last_state = p.value()
        
        # re-enable the interupt
        p.irq(self._pin_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        
        # did the value actually changed? 
        if self.value != self._state_to_value(last_state):    
            # set the value
            self._value = self._state_to_value(self._pin.value())
            
            # manage call backs
            if self._value and self._when_activated is not None:
                self._when_activated()
            elif not self._value and self._when_deactivated is not None:
                self._when_deactivated()
                    
    @property
    def value(self):
        return self._value
    
    @property
    def when_activated(self):
        return self._when_activated
    
    @when_activated.setter
    def when_activated(self, value):
        self._when_activated = value
        
    @property
    def when_deactivated(self):
        return self._when_deactivated
    
    @when_activated.setter
    def when_deactivated(self, value):
        self._when_deactivated = value
    
    def __del__(self):
        self._pin.irq(handler=None)
        
        
class Button(DigitalInputDevice):
    def __init__(self, pin, pull_up=True, bounce_time=0.02):
        super().__init__(pin=pin, pull_up=pull_up, bounce_time=bounce_time)
        
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated
