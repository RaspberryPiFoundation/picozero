from machine import Pin, PWM, Timer, ADC
from micropython import schedule
from time import ticks_ms, sleep

class PWMChannelAlreadyInUse(Exception):
    pass
        
class ValueChange:
    """
    Internal class to control the value of an output device 

    :param OutputDevice output_device:
        The OutputDevice object you wish to change the value of

    :param generator:
        A generator function which yields a 2d list of
        ((value, seconds), *).
        
        The output_device's value will be set for the number of
        seconds.

    :param int n:
        The number of times to repeat the sequence. If None, the
        sequence will repeat forever. 
    
    :param bool wait:
        If True the ValueChange object will block (wait) until
        the sequence has completed.
    """
    def __init__(self, output_device, generator, n, wait):
        self._output_device = output_device
        self._generator = generator
        self._n = n

        self._gen = self._generator()
        
        self._timer = Timer()
        self._running = True
        self._wait = wait
        
        self._set_value()
            
    def _set_value(self, timer_obj=None):
        if self._wait:
            # wait for the exection to end
            next_seq = self._get_value()
            while next_seq is not None:
                value, seconds = next_seq
                
                self._output_device._write(value)
                sleep(seconds)
                
                next_seq = self._get_value()
                
        else:
            # run the timer
            next_seq = self._get_value()
            if next_seq is not None:
                value, seconds = next_seq
                
                self._output_device._write(value)            
                self._timer.init(period=int(seconds * 1000), mode=Timer.ONE_SHOT, callback=self._set_value)

        if next_seq is None:
            # the sequence has finished, turn the device off
            self._output_device.off()
            self._running = False
                
    def _get_value(self):
        try:
            return next(self._gen)
            
        except StopIteration:
            
            self._n = self._n - 1 if self._n is not None else None
            if self._n == 0:
                # its the end, return None
                return None
            else:
                # recreate the generator and start again
                self._gen = self._generator()
                return next(self._gen)
        
    def stop(self):
        self._running = False
        self._timer.deinit()

###############################################################################
# OUTPUT DEVICES
###############################################################################

class OutputDevice:
    """
    Base class for output devices. 
    """   
    def __init__(self, active_high=True, initial_value=False):
        self.active_high = active_high
        if initial_value is not None:
            self._write(initial_value)
        self._value_changer = None
    
    @property
    def active_high(self):
        """
        Sets or returns the active_high property. If :data:`True`, the 
        :meth:`on` method will set the Pin to HIGH. If :data:`False`, 
        the :meth:`on` method will set the Pin toLOW (the :meth:`off` method 
        always does the opposite).
        """
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
        self._stop_change()
        self._write(value)
        
    def on(self):
        """
        Turns the device on.
        """
        self.value = 1

    def off(self):
        """
        Turns the device off.
        """
        self.value = 0
            
    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is on.
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
            
    def blink(self, on_time=1, off_time=None, n=None, wait=False):
        """
        Make the device turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds the device will be on. Defaults to 1.

        :param float off_time:
            The length of time in seconds the device will be off. Defaults to 1.

        :param int n:
            The number of times to repeat the blink operation. If None is 
            specified, the device will continue blinking forever. The default
            is None.

        :param bool wait:
           If True the method will block until the device stops turning on and off. 
           If False the method will return and the device will turn on and off in
           the background. Defaults to False.        
        """
        off_time = on_time if off_time is None else off_time
        
        self.off()
        self._start_change(lambda : iter([(1,on_time), (0,off_time)]), n, wait)
            
    def _start_change(self, generator, n, wait):
        self._value_changer = ValueChange(self, generator, n, wait)
    
    def _stop_change(self):
        if self._value_changer is not None:
            self._value_changer.stop()
            self._value_changer = None

    def close(self):
        """
        Turns the device off.
        """
        self.value = 0

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
                
    def close(self):
        """
        Closes the device and turns the device off. Once closed, the device
        can no longer be used.
        """
        super().close()
        self._pin = None
        
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
    """
    Represents an active or passive buzzer which can be turned on or off.

    :param int pin:
        The pin that the device is connected to.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the Buzzer will be off initially.  If
        :data:`True`, the Buzzer will be switched on initially.
    """
    pass

Buzzer.beep = Buzzer.blink

class PWMOutputDevice(OutputDevice):
    
    PIN_TO_PWM_CHANNEL = ["0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B","7A","7B","0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B"]
    _channels_used = {}
    
    def __init__(self, pin, freq=100, duty_factor=65535, active_high=True, initial_value=False):
        self._check_pwm_channel(pin)
        self._pin_num = pin
        self._duty_factor = duty_factor
        self._pwm = PWM(Pin(pin))
        self._pwm.freq(freq)
        super().__init__(active_high, initial_value)
        
    def _check_pwm_channel(self, pin_num):
        channel = PWMOutputDevice.PIN_TO_PWM_CHANNEL[pin_num]
        if channel in PWMOutputDevice._channels_used.keys():
            raise PWMChannelAlreadyInUse(
                f"PWM channel {channel} is already in use by pin {PWMOutputDevice._channels_used[channel]}. Use a different pin"
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
        """
        Returns :data:`True` if the device is on.
        """
        return self.value != 0

    @property
    def freq(self):
        """
        Returns the current frequency of the device.
        """
        return self._pwm.freq()
    
    @freq.setter
    def freq(self, freq):
        """
        Sets the frequency of the device.
        """
        self._pwm.freq(freq)

    def blink(self, on_time=1, off_time=None, n=None, wait=False, fade_in_time=0, fade_out_time=None, fps=25):
        """
        Make the device turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds the device will be on. Defaults to 1.

        :param float off_time:
            The length of time in seconds the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.

        :param int n:
            The number of times to repeat the blink operation. If `None`, the 
            device will continue blinking forever. The default is `None`.

        :param bool wait:
           If True the method will block until the LED stops blinking. If False
           the method will return and the LED is will blink in the background.
           Defaults to False.

        :param float fade_in_time:
            The length of time in seconds to spend fading in. Defaults to 0.

        :param float fade_out_time:
            The length of time in seconds to spend fading out. If `None`,
            it will be the same as ``fade_in_time``. Defaults to `None`.

        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states when fading. Defaults to 25.
        """
        self.off()
        
        off_time = on_time if off_time is None else off_time
        fade_out_time = fade_in_time if fade_out_time is None else fade_out_time
        
        def blink_generator():
            if fade_in_time > 0:
                for s in [
                    (i * (1 / fps) / fade_in_time, 1 / fps)
                    for i in range(int(fps * fade_in_time))
                    ]:
                    yield s
                
            if on_time > 0:
                yield (1, on_time)

            if fade_out_time > 0:
                for s in [
                    (1 - (i * (1 / fps) / fade_out_time), 1 / fps)
                    for i in range(int(fps * fade_out_time))
                    ]:
                    yield s
                
            if off_time > 0:
                 yield (0, off_time)
            
        self._start_change(blink_generator, n, wait)

    def pulse(self, fade_in_time=1, fade_out_time=None, n=None, wait=False, fps=25):
        """
        Make the device pulse on and off repeatedly.
        
        :param float fade_in_time:
            The length of time in seconds the device will take to turn on.
            Defaults to 1.

        :param float fade_out_time:
           The length of time in seconds the device will take to turn off.
           Defaults to 1.
           
        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states. Defaults to 25.
           
        :param int n:
           The number of times to pulse the LED. If None the LED will pulse
           forever. Defaults to None.
    
        :param bool wait:
           If True the method will block until the LED stops pulsing. If False
           the method will return and the LED is will pulse in the background.
           Defaults to False.
        """
        self.blink(on_time=0, off_time=0, fade_in_time=fade_in_time, fade_out_time=fade_out_time, n=n, wait=wait, fps=fps)

    def close(self):
        """
        Closes the device and turns the device off. Once closed, the device
        can no longer be used.
        """
        super().close()
        del PWMOutputDevice._channels_used[
            PWMOutputDevice.PIN_TO_PWM_CHANNEL[self._pin_num]
            ]
        self._pin.deinit()
        self._pin = None
    
class PWMLED(PWMOutputDevice):
    """
    Represents an LED driven by a PWM pin whose brightness can be changed.

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

class PWMBuzzer(PWMOutputDevice):
    """
    Represents a passive buzzer driven by a PWM pin whose volume can be changed.

    :param int pin:
        The pin that the device is connected to.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the buzzer will be off initially.  If
        :data:`True`, the buzzer will be switched on initially.
    """
    def __init__(self, pin, freq=100, duty_factor=1023, active_high=True, initial_value=False):
        self._volume = 1
        super().__init__(pin=pin,
            duty_factor=duty_factor,
            active_high=active_high,
            initial_value=initial_value)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        self.value = 1 if self._volume > 0 else 0
    
    def _write(self, value):
        super()._write(self._volume * value)
    
    def _read(self):
        return 1 if super()._read() > 0 else 0

PWMBuzzer.beep = Buzzer.blink

class Speaker(OutputDevice):
    NOTES = {
        'b0': 31, 'c1': 33, 'c#1': 35, 'd1': 37, 'd#1': 39, 'e1': 41, 'f1': 44, 'f#1': 46, 'g1': 49,'g#1': 52, 'a1': 55,
        'a#1': 58, 'b1': 62, 'c2': 65, 'c#2': 69, 'd2': 73, 'd#2': 78,
        'e2': 82, 'f2': 87, 'f#2': 93, 'g2': 98, 'g#2': 104, 'a2': 110, 'a#2': 117, 'b2': 123,
        'c3': 131, 'c#3': 139, 'd3': 147, 'd#3': 156, 'e3': 165, 'f3': 175, 'f#3': 185, 'g3': 196, 'g#3': 208, 'a3': 220, 'a#3': 233, 'b3': 247,
        'c4': 262, 'c#4': 277, 'd4': 294, 'd#4': 311, 'e4': 330, 'f4': 349, 'f#4': 370, 'g4': 392, 'g#4': 415, 'a4': 440,'a#4': 466,'b4': 494,
        'c5': 523, 'c#5': 554, 'd5': 587, 'd#5': 622, 'e5': 659, 'f5': 698, 'f#5': 740, 'g5': 784, 'g#5': 831, 'a5': 880, 'a#5': 932, 'b5': 988,
        'c6': 1047, 'c#6': 1109, 'd6': 1175, 'd#6': 1245, 'e6': 1319, 'f6': 1397, 'f#6': 1480, 'g6': 1568, 'g#6': 1661, 'a6': 1760, 'a#6': 1865, 'b6': 1976,
        'c7': 2093, 'c#7': 2217, 'd7': 2349, 'd#7': 2489,
        'e7': 2637, 'f7': 2794, 'f#7': 2960, 'g7': 3136, 'g#7': 3322, 'a7': 3520, 'a#7': 3729, 'b7': 3951,
        'c8': 4186, 'c#8': 4435, 'd8': 4699, 'd#8': 4978 
        }
    
    def __init__(self, pin, initial_freq=440, initial_volume=0, duty_factor=1023, active_high=True):
        
        self._pwm_buzzer = PWMBuzzer(
            pin,
            freq=initial_freq,
            duty_factor=duty_factor,
            active_high=active_high,
            initial_value=None,
            )
        
        super().__init__(active_high, None)
        self.volume = initial_volume
        
    def on(self, volume=1):
        self.volume = volume
        
    def off(self):
        self.volume = 0

    @property
    def value(self):
        """
        Sets or returns the value of the speaker. value is a tuple of (freq, volume).
        """
        return tuple(self.freq, self.volume)

    @value.setter
    def value(self, value):
        self._stop_change()
        self._write(value)

    @property
    def volume(self):
        """
        Sets or returns the volume of the speaker. 1 for max volume. 0 for off.
        """
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        self.value = (self.freq, self._volume)
        
    @property
    def freq(self):
        """
        Sets or returns the current frequency of the speaker.
        """
        return self._pwm_buzzer.freq
    
    @freq.setter
    def freq(self, freq):
        self._pwm_buzzer.freq(freq)

    def _write(self, value):
        # set the frequency
        self._pwm_buzzer.freq = value[0]
        
        # write the volume value
        self._pwm_buzzer.volume = value[1]

    def _to_freq(self, freq):
        if freq is not None and freq != '' and freq != 0: 
            if type(freq) is str:
                return int(self.NOTES[freq])
            elif freq <= 128 and freq > 0: # MIDI
                midi_factor = 2**(1/12)
                return int(440 * midi_factor ** (freq - 69))
            else:
                return freq
        else:
            return None

    def beep(self, on_time=1, off_time=None, n=None, wait=False, fade_in_time=0, fade_out_time=None, fps=25):
        """
        Make the buzzer turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds the device will be on. Defaults to 1.

        :param float off_time:
            The length of time in seconds the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.

        :param int n:
            The number of times to repeat the beep operation. If `None`, the 
            device will continue blinking forever. The default is `None`.

        :param bool wait:
           If True the method will block until the buzzer stops beeping. If False
           the method will return and the buzzer will beep in the background.
           Defaults to False.

        :param float fade_in_time:
            The length of time in seconds to spend fading in. Defaults to 0.

        :param float fade_out_time:
            The length of time in seconds to spend fading out. If `None`,
            it will be the same as ``fade_in_time``. Defaults to `None`.

        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states when fading. Defaults to 25.
        """
        self._pwm_buzzer.blink(on_time, off_time, n, wait, fade_in_time, fade_out_time, fps)

    def play(self, tune=440, duration=1, volume=1, n=1, wait=True):
        """
        Plays a tune for a given duration. 

        :param int tune:

            The tune to play which can be specified as:

                + a single "note", represented as:
                  + a frequency in Hz e.g. `440`
                  + a midi note e.g. `60`
                  + a note name as a string e.g `"E4"`
                + a list of single notes e.g. `[440, 60, "E4"]`
                + a list of 2 value tuples of (note, duration) e.g. `[(440,1), (60, 2), ("e4", 3)]`

            Defaults to `440`.
        
        :param int volume:
            The volume of the tune. 1 is max volume. 0 is mute. Defaults to 1.

        :param float duration:
            The duration of each note in seconds. Defaults to 1.

        :param int n:
           The number of times to play the tune. If None the tune will play
           forever. Defaults to 1.
    
        :param bool wait:
           If True the method will block until the tune has finished. If False
           the method will return and the tune will play in the background.
           Defaults to True.
        """

        # tune isnt a list, so it must be a single frequency or note
        if not isinstance(tune, (list, tuple)):
            tune = [(tune, duration)]

        def tune_generator():
            for note in tune:

                # note isnt a list or tuple, it must be a single frequency or note
                if not isinstance(note, (list, tuple)):
                    # make it into a tuple
                    note = (note, duration)

                # turn the notes in frequencies
                freq = self._to_freq(note[0])
                freq_duration = note[1]
                
                # if this is a tune of greater than 1 note, add gaps between notes
                if len(tune) == 1:
                    yield ((freq, volume), freq_duration)
                else:
                    yield ((freq, volume), freq_duration * 0.9)
                    yield ((freq, 0), freq_duration * 0.1)
                    
        self._start_change(tune_generator, n, wait)

class RGBLED(OutputDevice):
    """
    Extends :class:`OutputDevice` and represents a full color LED component (composed
    of red, green, and blue LEDs).
    Connect the common cathode (longest leg) to a ground pin; connect each of
    the other legs (representing the red, green, and blue anodes) to any GP
    pins.  You should use three limiting resistors (one per anode).
    The following code will make the LED yellow::

        from picozero import RGBLED
        rgb = RGBLED(1, 2, 3)
        rgb.color = (1, 1, 0)

    0-255 colours are also supported::

        rgb.color = (255, 255, 0)

    :type red: int
    :param red:
        The GP pin that controls the red component of the RGB LED. 
    :type green: int
    :param green:
        The GP pin that controls the green component of the RGB LED.
    :type blue: int
    :param blue:
        The GP pin that controls the blue component of the RGB LED.
    :param bool active_high:
        Set to :data:`True` (the default) for common cathode RGB LEDs. If you
        are using a common anode RGB LED, set this to :data:`False`.
    :type initial_value: ~colorzero.Color or tuple
    :param initial_value:
        The initial color for the RGB LED. Defaults to black ``(0, 0, 0)``.
    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMLED` instances for
        each component of the RGBLED. If :data:`False`, construct 
        :class:`DigitalLED` instances.
    
    """
    def __init__(self, red=None, green=None, blue=None, active_high=True,
                 initial_value=(0, 0, 0), pwm=True):
        self._leds = ()
        self._last = initial_value
        LEDClass = PWMLED if pwm else DigitalLED
        self._leds = tuple(
            LEDClass(pin, active_high=active_high)
            for pin in (red, green, blue))
        super().__init__(active_high, initial_value)
        
    def __del__(self):
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
        """
        Represents the color of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 1 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 1 if not).
        For example, red would be ``(1, 0, 0)`` and yellow would be ``(1, 1,
        0)``, while orange would be ``(1, 0.5, 0)``.
        """
        return tuple(led.brightness for led in self._leds)

    @value.setter
    def value(self, value):
        self._stop_change()
        self._write(value)

    @property
    def is_active(self):
        """
        Returns :data:`True` if the LED is currently active (not black) and
        :data:`False` otherwise.
        """
        return self.value != (0, 0, 0)

    is_lit = is_active

    def _to_255(self, value):
        return round(value * 255)
    
    def _from_255(self, value):
        return 0 if value == 0 else value / 255
    
    @property
    def color(self):
        """
        Represents the color of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 255 if not).
        For example, red would be ``(255, 0, 0)`` and yellow would be ``(255, 255,
        0)``, while orange would be ``(255, 127, 0)``.
        """
        return tuple(self._to_255(v) for v in self.value)

    @color.setter
    def color(self, value):
        self.value = tuple(self._from_255(v) for v in value)

    @property
    def red(self):
        """
        Represents the red component of the LED as value between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 255 if not).
        """
        return self._to_255(self.value[0])

    @red.setter
    def red(self, value):
        r, g, b = self.value
        self.value = self._from_255(value), g, b

    @property
    def green(self):
        """
        Represents the green component of the LED as value between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 255 if not).
        """
        return self._to_255(self.value[1])

    @green.setter
    def green(self, value):
        r, g, b = self.value
        self.value = r, self._from_255(value), b

    @property
    def blue(self):
        """
        Represents the blue component of the LED as value between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 255 if not).
        """
        return self._to_255(self.value[2])

    @blue.setter
    def blue(self, value):
        r, g, b = self.value
        self.value = r, g, self._from_255(value)

    def on(self):
        """
        Turn the LED on. This equivalent to setting the LED color to white
        ``(1, 1, 1)``.
        """
        self.value = (1, 1, 1)

    def invert(self):
        """
        Invert the state of the device. If the device is currently off
        (:attr:`value` is ``(0, 0, 0)``), this changes it to "fully" on
        (:attr:`value` is ``(1, 1, 1)``).  If the device has a specific color,
        this method inverts the color.
        """
        r, g, b = self.value
        self.value = (1 - r, 1 - g, 1 - b)
        
    def toggle(self):
        """
        Toggle the state of the device. If the device has a specific colour then save that colour and turn off. 
        If the device is off, change it to the last colour or, if none, to fully on (:attr:`value` is ``(1, 1, 1)``).
        """
        if self.value == (0, 0, 0):
            self.value = self._last or (1, 1, 1)
        else:
            self._last = self.value 
            self.value = (0, 0, 0)
            
    def blink(self, on_times=1, fade_times=0, colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), n=None, wait=False, fps=25):
        """
        Make the device blink between colours repeatedly.

        :param float on_times:
            Single value or tuple of numbers of seconds to stay on each colour. Defaults to 1 second. 
        :param float fade_times:
            Sinlge value or tuple of times to fade between each colour. Must be 0 if
            *pwm* was :data:`False` when the class was constructed.
        :type colors: tuple
            Tuple of colours to blink between, use ``(0, 0, 0)`` for off.
        :param colors:
            The colors to blink between. Defaults to red, green, blue.
        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.
        :param bool wait:
            If :data:`False` (the default), use a Timer to manage blinking
            continue blinking and return immediately. If :data:`False`, only
            return when the blink is finished (warning: the default value of
            *n* will result in this method never returning).
        """    
        self.off()
        
        if type(on_times) is not tuple:
            on_times = (on_times, ) * len(colors)
        if type(fade_times) is not tuple:
            fade_times = (fade_times, ) * len(colors)
        # If any value is above zero then treat all as 0-255 values
        if any(v > 1 for v in sum(colors, ())):
            colors = tuple(tuple(self._from_255(v) for v in t) for t in colors)
        
        def blink_generator():
        
            # Define a linear interpolation between
            # off_color and on_color
            
            lerp = lambda t, fade_in, color1, color2: tuple(
                (1 - t) * off + t * on
                if fade_in else
                (1 - t) * on + t * off
                for off, on in zip(color2, color1)
                )
            
            for c in range(len(colors)):
                if fade_times[c] > 0:
                    for i in range(int(fps * fade_times[c])):
                        v = lerp(i * (1 / fps) / fade_times[c], True, colors[(c + 1) % len(colors)], colors[c])
                        t = 1 / fps       
                        yield (v, t)
            
                if on_times[c] > 0:
                    yield (colors[c], on_times[c])
    
        self._start_change(blink_generator, n, wait)
            
    def pulse(self, fade_times=1, colors=((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)), n=None, wait=False, fps=25):
        """
        Make the device fade between colours repeatedly.

        :param float fade_times:
            Single value or tuple of numbers of seconds to spend fading. Defaults to 1.
        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.
        :type colors: tuple
        :param on_color:
            Tuple of colours to pulse between in order. Defaults to red, off, green, off, blue, off. 
        :type off_color: ~colorzero.Color or tuple
        :type n: int or None
        :param n:
            Number of times to pulse; :data:`None` (the default) means forever.
        """
        on_times = 0
        self.blink(on_times, fade_times, colors, n, wait, fps)
        
    def cycle(self, fade_times=1, colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), n=None, wait=False, fps=25):
        """
        Make the device fade in and out repeatedly.

        :param float fade_times:
            Single value or tuple of numbers of seconds to spend fading between colours. Defaults to 1.
        :param float fade_times:
            Number of seconds to spend fading out. Defaults to 1.
        :type colors: tuple
        :param on_color:
            Tuple of colours to cycle between. Defaults to red, green, blue. 
        :type n: int or None
        :param n:
            Number of times to cycle; :data:`None` (the default) means forever.
        """
        on_times = 0
        self.blink(on_times, fade_times, colors, n, wait, fps)

###############################################################################
# INPUT DEVICES
###############################################################################

class InputDevice:
    """
    Base class for input devices.
    """
    def __init__(self, active_state=None):
        self._active_state = active_state

    @property
    def active_state(self):
        """
        Sets or returns the active state of the device. If :data:`None` (the default),
        the device will return the value that the pin is set to. If
        :data:`True`, the device will return :data:`True` if the pin is
        HIGH. If :data:`False`, the device will return :data:`False` if the
        pin is LOW.
        """
        return self._active_state

    @active_state.setter
    def active_state(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True
        
    @property
    def value(self):
        """
        Returns the current value of the device. This is either :data:`True` 
        or :data:`False` depending on the value of :attr:`active_state`.
        """
        return self._read()

class DigitalInputDevice(InputDevice):
    """
    Represents a generic input device with digital functionality e.g. buttons 
    which can be either active or inactive.

    :param int pin:
        The pin that the device is connected to.

    :param bool pull_up:
        If :data:`True` (the default), the device will be pulled up to
        HIGH. If :data:`False`, the device will be pulled down to LOW.

    :param bool active_state:
        If :data:`True` (the default), the device will return :data:`True`
        if the pin is HIGH. If :data:`False`, the device will return
        :data:`False` if the pin is LOW.

    :param float bounce_time:
        The bounce time for the device. If set, the device will ignore
        any button presses that happen within the bounce time after a
        button release. This is useful to prevent accidental button
        presses from registering as multiple presses.
    """
    def __init__(self, pin, pull_up=False, active_state=None, bounce_time=None):
        super().__init__(active_state)
        self._pin = Pin(
            pin,
            mode=Pin.IN,
            pull=Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self._bounce_time = bounce_time
        
        if active_state is None:
            self._active_state = False if pull_up else True
        else:
            self._active_state = active_state
        
        self._state = self._pin.value()
        
        self._when_activated = None
        self._when_deactivated = None
        
        # setup interupt
        self._pin.irq(self._pin_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        
    def _state_to_value(self, state):
        return int(bool(state) == self._active_state)
    
    def _read(self):
        return self._state_to_value(self._state)

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
        if self._state != last_state:
            # set the state
            self._state = self._pin.value()
            
            def schedule_callback(callback):
                callback()
            
            # manage call backs
            if self.value and self._when_activated is not None:
                schedule(schedule_callback, self._when_activated)
                
            elif not self.value and self._when_deactivated is not None:
                schedule(schedule_callback, self._when_deactivated)
                    
    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is active.
        """
        return bool(self.value)

    @property
    def is_inactive(self):
        """
        Returns :data:`True` if the device is inactive.
        """
        return not bool(self.value)
    
    @property
    def when_activated(self):
        """
        Returns a :samp:`callback` that will be called when the device is activated.
        """
        return self._when_activated
    
    @when_activated.setter
    def when_activated(self, value):
        self._when_activated = value
        
    @property
    def when_deactivated(self):
        """
        Returns a :samp:`callback` that will be called when the device is deactivated.
        """
        return self._when_deactivated
    
    @when_activated.setter
    def when_deactivated(self, value):
        self._when_deactivated = value
    
    def close(self):
        """
        Closes the device and releases any resources. Once closed, the device
        can no longer be used.
        """
        self._pin.irq(handler=None)
        self._pin = None

class Switch(DigitalInputDevice):
    """
    Represents a toggle switch which is either open or closed.

    :param int pin:
        The pin that the device is connected to.

    :param bool pull_up:
        If :data:`True` (the default), the device will be pulled up to
        HIGH. If :data:`False`, the device will be pulled down to LOW.

    :param float bounce_time:
        The bounce time for the device. If set, the device will ignore
        any button presses that happen within the bounce time after a
        button release. This is useful to prevent accidental button
        presses from registering as multiple presses. Defaults to 0.02 
        seconds.
    """
    def __init__(self, pin, pull_up=True, bounce_time=0.02): 
        super().__init__(pin=pin, pull_up=pull_up, bounce_time=bounce_time)

Switch.is_closed = Switch.is_active
Switch.is_open = Switch.is_inactive
Switch.when_closed = Switch.when_activated
Switch.when_opened = Switch.when_deactivated

class Button(Switch):
    """
    Represents a push button which can be either pressed or released.

    :param int pin:
        The pin that the device is connected to.

    :param bool pull_up:
        If :data:`True` (the default), the device will be pulled up to
        HIGH. If :data:`False`, the device will be pulled down to LOW.

    :param float bounce_time:
        The bounce time for the device. If set, the device will ignore
        any button presses that happen within the bounce time after a
        button release. This is useful to prevent accidental button
        presses from registering as multiple presses. Defaults to 0.02 
        seconds.
    """
    pass

Button.is_pressed = Button.is_active
Button.is_released = Button.is_inactive
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated 

class AnalogInputDevice(InputDevice):
    def __init__(self, pin, active_state=True, threshold=0.5):
        super().__init__(active_state)
        self._adc = ADC(pin)
        self._threshold = float(threshold)
        
    def _state_to_value(self, state):
        return (state if self.active_state else 1 - state) / 65535

    def _value_to_state(self, value):
        return int(65535 * (value if self.active_state else 1 - value))
    
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
    def __init__(self, pin, active_state=True, threshold=0.5, conversion=None):
         self._conversion = conversion
         super().__init__(pin, active_state, threshold)
        
    @property
    def temp(self):
        if self._conversion is not None:
            return self._conversion(self.voltage)
        else:
            return None
       
pico_temp_sensor = TemperatureSensor(4, True, 0.5, pico_temp_conversion)
TempSensor = TemperatureSensor
Thermistor = TemperatureSensor


