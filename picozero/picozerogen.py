from machine import Pin, PWM, Timer, ADC
from time import ticks_ms, sleep
import micropython

class PWMChannelAlreadyInUse(Exception):
    pass

class AsyncValueChange:
    """
    Internal class to control the value of an output device 
    asynchronously
    :param OutputDevice output_device:
        The OutputDevice object you wish to change the value of
    :param sequence:
        A 2d list of ((value, seconds), *).
        
        The output_device's value will be set for the number of
        seconds.
    """
    def __init__(self, output_device):
        self._output_device = output_device
        self._timer = Timer()

    def set_generator(self, generator):
        self.stop()
        self._generator = generator
        self._set_value()
        
    def _set_value(self, timer_obj=None):
        try:
            next_seq = next(self._generator)
            print(next_seq)
            value, seconds = next_seq
            self._output_device.value = value
            self._timer.init(period=int(seconds * 1000), mode=Timer.ONE_SHOT, callback=self._set_value)
        except StopIteration:
            # the sequence has finished, set the value to 0
            self.stop()
            self._output_device.value = 0
        
    def stop(self):
        self._timer.deinit()
        print("Stop")

        
class OutputDevice:
    
    def __init__(self, active_high=True, initial_value=False):
        self.active_high = active_high
        self._write(initial_value)
        self._async_change = AsyncValueChange(self)
    
    @property
    def active_high(self):
        return self._active_state

    @active_high.setter
    def active_high(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True
        
    @property
    def value(self):
        """
        Sets or returns a value representing the state of the device. 1 is on, 0 is off.
        """
        return self._read()

    @value.setter
    def value(self, value):
        self._write(value)
        
    def on(self):
        """
        Turns the device on.
        """
        self._stop_async()
        self.value = 1

    def off(self):
        """
        Turns the device off.
        """
        self._stop_async()
        self.value = 0
            
    @property
    def is_active(self):
        """
        Returns :data:`True` is the device is on.
        """
        return bool(self.value)

    def toggle(self):
        """
        If the device is off, turn it on. If it is on, turn it off.
        """
        if self.is_active:
            self.off()
        else:
            self.on()
            
    def blink(self, on_time=1, off_time=None, n=None):
        """
        Make the device turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds the device will be on. Defaults to 1.
        :param float off_time:
            The length of time in seconds the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.
        :param int n:
            The number of times to repeat the blink operation. If None is 
            specified, the device will continue blinking forever. The default
            is None.
        """
        off_time = on_time if off_time is None else off_time
        
        self._stop_async()
        self._start_async([(1,on_time), (0,off_time)], n)
        
    def _start_async(self, generator):
        self._async_change.set_generator(generator)

    def _stop_async(self):
        self._async_change.stop()
            
    def __del__(self):
        self._stop_async()

class DigitalOutputDevice(OutputDevice):
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
    """
    Represents a simple LED which can be switched on and off.
    :param int pin:
        The pin that the device is connected to.
    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).
    :param bool initial_value:
        If :data:`False` (the default), the LED will be off initially.  If
        :data:`True`, the LED will be switched on initially.
    """
    pass

DigitalLED.is_lit = DigitalLED.is_active

class Buzzer(DigitalOutputDevice):
    pass

Buzzer.beep = Buzzer.blink

class PWMOutputDevice(OutputDevice):
    
    PIN_TO_PWM_CHANNEL = ["0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B","7A","7B","0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B"]
    _channels_used = {}
    
    def __init__(self, pin, freq=100, duty_factor=65025, active_high=True, initial_value=False):
        self._check_pwm_channel(pin)
        self._pin_num = pin
        self._duty_factor = duty_factor
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
        return (state if self.active_high else 1 - state) / self._duty_factor

    def _value_to_state(self, value):
        return int(self._duty_factor * (value if self.active_high else 1 - value))
    
    def _read(self):
        return self._state_to_value(self._pwm.duty_u16())
    
    def _write(self, value):
        self._pwm.duty_u16(self._value_to_state(value))
        
    @property
    def is_active(self):
        return self.value != 0
    
    def __del__(self):
        del PWMOutputDevice._channels_used[
            PWMOutputDevice.PIN_TO_PWM_CHANNEL[self._pin_num]
            ]
    
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

    def blink(self, on_time=1, off_time=None, fade_in_time=0, fade_out_time=None, n=None, fps=25):
        """
        Make the device turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds the device will be on. Defaults to 1.
        :param float off_time:
            The length of time in seconds the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.
        :param float fade_in_time:
            The length of time in seconds to spend fading in. Defaults to 0.
        :param float fade_out_time:
            The length of time in seconds to spend fading out. If `None`,
            it will be the same as ``fade_in_time``. Defaults to `None`.
        :param int n:
            The number of times to repeat the blink operation. If `None`, the 
            device will continue blinking forever. The default is `None`.
        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states when fading. Defaults to 25.
        """
        self._stop_async()
        
        off_time = on_time if off_time is None else off_time
        fade_out_time = fade_in_time if fade_out_time is None else fade_out_time

        # build the blink sequence
        sequence = []

        if fade_in_time > 0:
            sequence += [
                (i * (1 / fps) / fade_in_time, 1 / fps)
                for i in range(int(fps * fade_in_time))
                ]
            
        if on_time > 0:
            sequence.append((1, on_time))

        if fade_out_time > 0:
            sequence += [
                (1 - (i * (1 / fps) / fade_out_time), 1 / fps)
                for i in range(int(fps * fade_out_time))
                ]
            
        if off_time > 0:
            sequence.append((0, off_time))
            
        self._start_async(sequence, n)

    def pulse(self, fade_in_time=1, fade_out_time=None, n=None, fps=25):
        """
        Make the device pulse on and off repeatedly.
        
        :param float fade_in_time:
            The length of time in seconds to spend fading in. Defaults to 0.
        :param float fade_out_time:
            The length of time in seconds to spend fading out. If `None`,
            it will be the same as ``fade_in_time``. Defaults to `None`.
        :param int n:
            The number of times to repeat the blink operation. If `None`, the 
            device will continue blinking forever. The default is `None`.
        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states when fading. Defaults to 25.
        """
        self.blink(on_time=0, off_time=0, fade_in_time=fade_in_time, fade_out_time=fade_out_time, n=n, fps=fps)
    
# factory for returning an LED
def LED(pin, use_pwm=True, active_high=True, initial_value=False):
    """
    Returns an instance of :class:`DigitalLED` or :class:`PWMLED` depending on
    the value of `use_pwm` parameter. 
    ::
        from picozero import LED
        my_pwm_led = LED(1)
        my_digital_led = LED(2, use_pwm=False)
    :param int pin:
        The pin that the device is connected to.
    :param int pin:
        If `use_pwm` is :data:`True` (the default), a :class:`PWMLED` will be
        returned. If `use_pwm` is :data:`False`, a :class:`DigitalLED` will be
        returned. A :class:`PWMLED` can control the brightness of the LED but
        uses 1 PWM channel.
    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).
    :param bool initial_value:
        If :data:`False` (the default), the device will be off initially.  If
        :data:`True`, the device will be switched on initially.
    """
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

pico_led = LED(25)

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
    def is_active(self):
        return bool(self.value)

    @property
    def is_inactive(self):
        return not bool(self.value)
    
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
        
        
class Switch(DigitalInputDevice):
    def __init__(self, pin, pull_up=True, bounce_time=0.02):
        super().__init__(pin=pin, pull_up=pull_up, bounce_time=bounce_time)

Switch.is_closed = Switch.is_active
Switch.is_open = Switch.is_inactive
Switch.when_closed = Switch.when_activated
Switch.when_opened = Switch.when_deactivated

class Button(Switch):
    pass

Button.is_pressed = Button.is_active
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated 

class RGBLED(OutputDevice):
    def __init__(self, red=None, green=None, blue=None, active_high=True,
                 initial_value=(0, 0, 0), pwm=True):
        self._leds = ()
        self._last = initial_value
        LEDClass = PWMLED if pwm else DigitalLED
        self._leds = tuple(
            LEDClass(pin, active_high=active_high)
            for pin in (red, green, blue))
        super().__init__(active_high, initial_value)
        self._stop_async()
        
    def __del__(self):
        self._stop_async()
        if getattr(self, '_leds', None):
            self._stop_blink()
            for led in self._leds:
                led.__del__()
        self._leds = ()
        super().__del__()

    def _write(self, value):
        if type(value) is not tuple:
            value = (value, ) * 3       
        for led, v in zip(self._leds, value):
            led.brightness = v
        
    @property
    def value(self):
        return tuple(led.brightness for led in self._leds)

    @value.setter
    def value(self, value):
        self._write(value)

    @property
    def is_active(self):
        return self.value != (0, 0, 0)

    is_lit = is_active

    def _to_255(self, value):
        return round(value * 255)
    
    def _from_255(self, value):
        return 0 if value == 0 else value / 255
    
    @property
    def color(self):
        return tuple(self._to_255(v) for v in self.value)

    @color.setter
    def color(self, value):
        self._stop_async()
        self.value = tuple(self._from_255(v) for v in value)

    @property
    def red(self):
        return self._to_255(self.value[0])

    @red.setter
    def red(self, value):
        r, g, b = self.value
        self.value = self._from_255(value), g, b

    @property
    def green(self):
        return self._to_255(self.value[1])

    @green.setter
    def green(self, value):
        r, g, b = self.value
        self.value = r, self._from_255(value), b

    @property
    def blue(self):
        return self._to_255(self.value[2])

    @blue.setter
    def blue(self, value):
        r, g, b = self.value
        self.value = r, g, self._from_255(value)

    def on(self):
        self.value = (1, 1, 1)

    def off(self):
        self._stop_async()
        self.value = (0, 0, 0)

    def invert(self):
        r, g, b = self.value
        self.value = (1 - r, 1 - g, 1 - b)
        
    def toggle(self):
        if self.value == (0, 0, 0):
            self.value = self._last or (1, 1, 1)
        else:
            self._last = self.value 
            self.value = (0, 0, 0)

    def _blink(self, args):
        print("Blink start")
        on_times, fade_times, colors, n, fps = args
        print(n)
        self._stop_async()
        if type(on_times) is not tuple:
            on_times = (on_times, ) * len(colors)
        if type(fade_times) is not tuple:
            fade_times = (fade_times, ) * len(colors)
                    
        # If any value is above zero then treat all as 0-255 values
        if any(v > 1 for v in sum(colors, ())):
            colors = tuple(tuple(self._from_255(v) for v in t) for t in colors)
        
        # Define a linear interpolation between
        # off_color and on_color
             
        def generator(on_times, fade_times, colors, n, fps):
            lerp = lambda t, fade_in, color1, color2: tuple(
                (1 - t) * off + t * on
                if fade_in else
                (1 - t) * on + t * off
                for off, on in zip(color2, color1)
                )
    
            while n != 0:
                for c in range(len(colors)):            
                    if fade_times[c] > 0:
                        for i in range(int(fps * fade_times[c])):
                            v = lerp(i * (1 / fps) / fade_times[c], True, colors[(c + 1) % len(colors)], colors[c])
                            t = 1 / fps       
                            yield (v, t)
            
                    if on_times[c] > 0:
                        yield ((colors[(c + 1) % len(colors)], on_times[c]))
            
                n = n - 1 if n is not None else None
                
        self._stop_async()
        
        self._start_async(generator(on_times, fade_times, colors, n, fps))

    def blink(self, on_times=1, fade_times=0, colors=((1, 1, 1), (0, 0, 0)), n=None, fps=25):
            
        try:
            micropython.schedule(self._blink, (on_times, fade_times, colors, n, fps))
        except:
            print("Schedule queue full")
            pass # Could raise an exception?
        
    def pulse(self, fade_times=1, colors=((1, 1, 1), (0, 0, 0)), n=None, fps=25):
        """
        Make the device fade in and out repeatedly.
        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 1.
        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.
        :type on_color: ~colorzero.Color or tuple
        :param on_color:
            The color to use when the LED is "on". Defaults to white.
        :type off_color: ~colorzero.Color or tuple
        :param off_color:
            The color to use when the LED is "off". Defaults to black.
        :type n: int or None
        :param n:
            Number of times to pulse; :data:`None` (the default) means forever.
        """
        on_times = 0
        self.blink(on_times, fade_times, colors, n, fps)
        
    def cycle(self, fade_times=1, colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), n=None, fps=25):
        """
        Make the device fade in and out repeatedly.
        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 1.
        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.
        :type on_color: ~colorzero.Color or tuple
        :param on_color:
            The color to use when the LED is "on". Defaults to white.
        :type off_color: ~colorzero.Color or tuple
        :param off_color:
            The color to use when the LED is "off". Defaults to black.
        :type n: int or None
        :param n:
            Number of times to pulse; :data:`None` (the default) means forever.
        """
        on_times = 0
        self.blink(on_times, fade_times, colors, n, fps)

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

def pico_temp_conversion(voltage):
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
       
pico_temp_sensor = TemperatureSensor(4, True, 0.5, pico_temp_conversion)
TempSensor = TemperatureSensor
Thermistor = TemperatureSensor

class PWMBuzzer(PWMOutputDevice):
    
    def __init__(self, pin, freq=440, active_high=True, initial_value=False, duty_factor=1023):    
        super().__init__(
            pin, 
            freq=freq, 
            duty_factor=duty_factor, 
            active_high=active_high, 
            initial_value=initial_value)
        
    def play(self, freq=440, duration=1, volume=1):

        self._pwm.freq(freq)

        if volume is not None:
            self.value = volume

        if duration is not None:
            sleep(duration)
            self.value = 0
        
    def on(self, freq=None):
        if freq is not None:
            self._pwm.freq(freq)

        self.value = 1

    def stop(self):
        self.value = 0
                
    def __del__(self):
        self.stop()
        super().__del__()

PWMBuzzer.volume = PWMBuzzer.value
PWMBuzzer.beep = PWMBuzzer.blink

def Speaker(pin, use_tones=True, active_high=True, initial_value=False, duty_factor=1023):
    if use_tones:
        return PWMBuzzer(pin, freq=440, active_high=active_high, initial_value=initial_value, duty_factor=duty_factor)
    else:
        return Buzzer(pin, active_high=active_high, initial_value=initial_value)
