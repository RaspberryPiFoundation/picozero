from machine import Pin, PWM, Timer, ADC
from micropython import schedule
from time import ticks_ms, ticks_us, sleep

###############################################################################
# EXCEPTIONS
###############################################################################


class PWMChannelAlreadyInUse(Exception):
    pass


class EventFailedScheduleQueueFull(Exception):
    pass


###############################################################################
# SUPPORTING CLASSES
###############################################################################


def clamp(n, low, high):
    return max(low, min(n, high))


def pinout(output=True):







    pins = """        ---usb---
GP0  1  |o     o| 40  VBUS
GP1  2  |o     o| 39  VSYS
GND  3  |o     o| 38  GND
GP2  4  |o     o| 37  3V3_EN
GP3  5  |o     o| 36  3V3(OUT)
GP4  6  |o     o| 35           ADC_VREF
GP5  7  |o     o| 34  GP28     ADC2
GND  8  |o     o| 33  GND      AGND
GP6  9  |o     o| 32  GP27     ADC1
GP7  10 |o     o| 31  GP26     ADC0
GP8  11 |o     o| 30  RUN
GP9  12 |o     o| 29  GP22
GND  13 |o     o| 28  GND
GP10 14 |o     o| 27  GP21
GP11 15 |o     o| 26  GP20
GP12 16 |o     o| 25  GP19
GP13 17 |o     o| 24  GP18
GND  18 |o     o| 23  GND
GP14 19 |o     o| 22  GP17
GP15 20 |o     o| 21  GP16
        ---------"""

    if output:
        print(pins)
    return pins


class PinMixin:




    @property
    def pin(self):



        return self._pin_num

    def __str__(self):
        return "{} (pin {})".format(self.__class__.__name__, self._pin_num)


class PinsMixin:




    @property
    def pins(self):



        return self._pin_nums

    def __str__(self):
        return "{} (pins - {})".format(self.__class__.__name__, self._pin_nums)


class ValueChange:






















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
                self._timer.init(
                    period=int(seconds * 1000),
                    mode=Timer.ONE_SHOT,
                    callback=self._set_value,
                )

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
                # it's the end, return None
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




    def __init__(self, active_high=True, initial_value=False):
        self.active_high = active_high
        if initial_value is not None:
            self._write(initial_value)
        self._value_changer = None

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
        self._stop_change()
        self._write(value)

    def on(self, value=1, t=None, wait=False):
















        if t is None:
            self.value = value
        else:
            self._start_change(
                lambda: iter(
                    [
                        (value, t),
                    ]
                ),
                1,
                wait,
            )

    def off(self):



        self.value = 0

    @property
    def is_active(self):



        return bool(self.value)

    def toggle(self):



        if self.is_active:
            self.off()
        else:
            self.on()

    def blink(self, on_time=1, off_time=None, n=None, wait=False):




















        off_time = on_time if off_time is None else off_time

        self.off()

        # is there anything to change?
        if on_time > 0 or off_time > 0:
            self._start_change(lambda: iter([(1, on_time), (0, off_time)]), n, wait)

    def _start_change(self, generator, n, wait):
        self._value_changer = ValueChange(self, generator, n, wait)

    def _stop_change(self):
        if self._value_changer is not None:
            self._value_changer.stop()
            self._value_changer = None

    def close(self):



        self.value = 0


class DigitalOutputDevice(OutputDevice, PinMixin):
















    def __init__(self, pin, active_high=True, initial_value=False):
        self._pin_num = pin
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




        super().close()
        self._pin = None


class DigitalLED(DigitalOutputDevice):
















    pass


DigitalLED.is_lit = DigitalLED.is_active


class Buzzer(DigitalOutputDevice):
















    pass


Buzzer.beep = Buzzer.blink


class PWMOutputDevice(OutputDevice, PinMixin):























    PIN_TO_PWM_CHANNEL = [
        "0A",
        "0B",
        "1A",
        "1B",
        "2A",
        "2B",
        "3A",
        "3B",
        "4A",
        "4B",
        "5A",
        "5B",
        "6A",
        "6B",
        "7A",
        "7B",
        "0A",
        "0B",
        "1A",
        "1B",
        "2A",
        "2B",
        "3A",
        "3B",
        "4A",
        "4B",
        "5A",
        "5B",
        "6A",
        "6B",
    ]
    _channels_used = {}

    def __init__(
        self, pin, freq=100, duty_factor=65535, active_high=True, initial_value=False
    ):
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
                "PWM channel {} is already in use by {}. Use a different pin".format(
                    channel, str(PWMOutputDevice._channels_used[channel])
                )
            )
        else:
            PWMOutputDevice._channels_used[channel] = self

    def _state_to_value(self, state):
        return (
            state if self.active_high else self._duty_factor - state
        ) / self._duty_factor

    def _value_to_state(self, value):
        return int(self._duty_factor * (value if self.active_high else 1 - value))

    def _read(self):
        return self._state_to_value(self._pwm.duty_u16())

    def _write(self, value):
        self._pwm.duty_u16(self._value_to_state(value))

    @property
    def is_active(self):



        return self.value != 0

    @property
    def freq(self):



        return self._pwm.freq()

    @freq.setter
    def freq(self, freq):



        self._pwm.freq(freq)

    def blink(
        self,
        on_time=1,
        off_time=None,
        n=None,
        wait=False,
        fade_in_time=0,
        fade_out_time=None,
        fps=25,
    ):






























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

        # is there anything to change?
        if on_time > 0 or off_time > 0 or fade_in_time > 0 or fade_out_time > 0:
            self._start_change(blink_generator, n, wait)

    def pulse(self, fade_in_time=1, fade_out_time=None, n=None, wait=False, fps=25):
























        self.blink(
            on_time=0,
            off_time=0,
            fade_in_time=fade_in_time,
            fade_out_time=fade_out_time,
            n=n,
            wait=wait,
            fps=fps,
        )

    def close(self):




        super().close()
        del PWMOutputDevice._channels_used[
            PWMOutputDevice.PIN_TO_PWM_CHANNEL[self._pin_num]
        ]
        self._pwm.deinit()
        self._pwm = None


class PWMLED(PWMOutputDevice):
    pass























PWMLED.brightness = PWMLED.value


def LED(pin, pwm=True, active_high=True, initial_value=False):






























    if pwm:
        return PWMLED(pin=pin, active_high=active_high, initial_value=initial_value)
    else:
        return DigitalLED(pin=pin, active_high=active_high, initial_value=initial_value)


try:
    pico_led = LED("LED", pwm=False)
except TypeError:
    # older version of micropython before "LED" was supported
    pico_led = LED(25, pwm=False)


class PWMBuzzer(PWMOutputDevice):























    def __init__(
        self, pin, freq=440, duty_factor=1023, active_high=True, initial_value=False
    ):
        super().__init__(pin, freq, duty_factor, active_high, initial_value)


PWMBuzzer.volume = PWMBuzzer.value
PWMBuzzer.beep = PWMBuzzer.blink


class Speaker(OutputDevice, PinMixin):























    NOTES = {
        "b0": 31,
        "c1": 33,
        "c#1": 35,
        "d1": 37,
        "d#1": 39,
        "e1": 41,
        "f1": 44,
        "f#1": 46,
        "g1": 49,
        "g#1": 52,
        "a1": 55,
        "a#1": 58,
        "b1": 62,
        "c2": 65,
        "c#2": 69,
        "d2": 73,
        "d#2": 78,
        "e2": 82,
        "f2": 87,
        "f#2": 93,
        "g2": 98,
        "g#2": 104,
        "a2": 110,
        "a#2": 117,
        "b2": 123,
        "c3": 131,
        "c#3": 139,
        "d3": 147,
        "d#3": 156,
        "e3": 165,
        "f3": 175,
        "f#3": 185,
        "g3": 196,
        "g#3": 208,
        "a3": 220,
        "a#3": 233,
        "b3": 247,
        "c4": 262,
        "c#4": 277,
        "d4": 294,
        "d#4": 311,
        "e4": 330,
        "f4": 349,
        "f#4": 370,
        "g4": 392,
        "g#4": 415,
        "a4": 440,
        "a#4": 466,
        "b4": 494,
        "c5": 523,
        "c#5": 554,
        "d5": 587,
        "d#5": 622,
        "e5": 659,
        "f5": 698,
        "f#5": 740,
        "g5": 784,
        "g#5": 831,
        "a5": 880,
        "a#5": 932,
        "b5": 988,
        "c6": 1047,
        "c#6": 1109,
        "d6": 1175,
        "d#6": 1245,
        "e6": 1319,
        "f6": 1397,
        "f#6": 1480,
        "g6": 1568,
        "g#6": 1661,
        "a6": 1760,
        "a#6": 1865,
        "b6": 1976,
        "c7": 2093,
        "c#7": 2217,
        "d7": 2349,
        "d#7": 2489,
        "e7": 2637,
        "f7": 2794,
        "f#7": 2960,
        "g7": 3136,
        "g#7": 3322,
        "a7": 3520,
        "a#7": 3729,
        "b7": 3951,
        "c8": 4186,
        "c#8": 4435,
        "d8": 4699,
        "d#8": 4978,
    }

    def __init__(
        self,
        pin,
        initial_freq=440,
        initial_volume=0,
        duty_factor=1023,
        active_high=True,
    ):

        self._pin_num = pin
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



        return tuple(self.freq, self.volume)

    @value.setter
    def value(self, value):
        self._stop_change()
        self._write(value)

    @property
    def volume(self):



        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        self.value = (self.freq, self.volume)

    @property
    def freq(self):



        return self._pwm_buzzer.freq

    @freq.setter
    def freq(self, freq):
        self.value = (freq, self.volume)

    def _write(self, value):
        # set the frequency
        if value[0] is not None:
            self._pwm_buzzer.freq = value[0]

        # write the volume value
        if value[1] is not None:
            self._pwm_buzzer.volume = value[1]

    def _to_freq(self, freq):
        if freq is not None and freq != "" and freq != 0:
            if type(freq) is str:
                return int(self.NOTES[freq])
            elif freq <= 128 and freq > 0:  # MIDI
                midi_factor = 2 ** (1 / 12)
                return int(440 * midi_factor ** (freq - 69))
            else:
                return freq
        else:
            return None

    def beep(
        self,
        on_time=1,
        off_time=None,
        n=None,
        wait=False,
        fade_in_time=0,
        fade_out_time=None,
        fps=25,
    ):






























        self._pwm_buzzer.blink(
            on_time, off_time, n, wait, fade_in_time, fade_out_time, fps
        )

    def play(self, tune=440, duration=1, volume=1, n=1, wait=True):
































        self.off()

        # tune isn't a list, so it must be a single frequency or note
        if not isinstance(tune, (list, tuple)):
            tune = [(tune, duration)]
        # if the first element isn't a list, then it must be list of a single note and duration
        elif not isinstance(tune[0], (list, tuple)):
            tune = [tune]

        def tune_generator():
            for note in tune:

                # note isn't a list or tuple, it must be a single frequency or note
                if not isinstance(note, (list, tuple)):
                    # make it into a tuple
                    note = (note, duration)

                # turn the notes into frequencies
                freq = self._to_freq(note[0])
                freq_duration = note[1]
                freq_volume = volume if freq is not None else 0

                # if this is a tune of greater than 1 note, add gaps between notes
                if len(tune) == 1:
                    yield ((freq, freq_volume), freq_duration)
                else:
                    yield ((freq, freq_volume), freq_duration * 0.9)
                    yield ((freq, 0), freq_duration * 0.1)

        self._start_change(tune_generator, n, wait)

    def close(self):
        self._pwm_buzzer.close()


class RGBLED(OutputDevice, PinsMixin):






































    def __init__(
        self,
        red=None,
        green=None,
        blue=None,
        active_high=True,
        initial_value=(0, 0, 0),
        pwm=True,
    ):
        self._pin_nums = (red, green, blue)
        self._leds = ()
        self._last = initial_value
        LEDClass = PWMLED if pwm else DigitalLED
        self._leds = tuple(
            LEDClass(pin, active_high=active_high) for pin in (red, green, blue)
        )
        super().__init__(active_high, initial_value)

    def _write(self, value):
        if type(value) is not tuple:
            value = (value,) * 3
        for led, v in zip(self._leds, value):
            led.value = v

    @property
    def value(self):







        return tuple(led.value for led in self._leds)

    @value.setter
    def value(self, value):
        self._stop_change()
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

    def invert(self):






        r, g, b = self.value
        self.value = (1 - r, 1 - g, 1 - b)

    def toggle(self):




        if self.value == (0, 0, 0):
            self.value = self._last or (1, 1, 1)
        else:
            self._last = self.value
            self.value = (0, 0, 0)

    def blink(
        self,
        on_times=1,
        fade_times=0,
        colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        n=None,
        wait=False,
        fps=25,
    ):





















        self.off()

        if type(on_times) is not tuple:
            on_times = (on_times,) * len(colors)
        if type(fade_times) is not tuple:
            fade_times = (fade_times,) * len(colors)
        # If any value is above zero then treat all as 0-255 values
        if any(v > 1 for v in sum(colors, ())):
            colors = tuple(tuple(self._from_255(v) for v in t) for t in colors)

        def blink_generator():

            # Define a linear interpolation between
            # off_color and on_color

            lerp = lambda t, fade_in, color1, color2: tuple(
                (1 - t) * off + t * on if fade_in else (1 - t) * on + t * off
                for off, on in zip(color2, color1)
            )

            for c in range(len(colors)):
                if on_times[c] > 0:
                    yield (colors[c], on_times[c])

                if fade_times[c] > 0:
                    for i in range(int(fps * fade_times[c])):
                        v = lerp(
                            i * (1 / fps) / fade_times[c],
                            True,
                            colors[(c + 1) % len(colors)],
                            colors[c],
                        )
                        t = 1 / fps
                        yield (v, t)

        self._start_change(blink_generator, n, wait)

    def pulse(
        self,
        fade_times=1,
        colors=((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)),
        n=None,
        wait=False,
        fps=25,
    ):















        on_times = 0
        self.blink(on_times, fade_times, colors, n, wait, fps)

    def cycle(
        self,
        fade_times=1,
        colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        n=None,
        wait=False,
        fps=25,
    ):














        on_times = 0
        self.blink(on_times, fade_times, colors, n, wait, fps)

    def close(self):
        super().close()
        for led in self._leds:
            led.close()
        self._leds = None


RGBLED.colour = RGBLED.color


class Motor(PinsMixin):




















    def __init__(self, forward, backward, pwm=True):
        self._pin_nums = (forward, backward)
        self._forward = (
            PWMOutputDevice(forward) if pwm else DigitalOutputDevice(forward)
        )
        self._backward = (
            PWMOutputDevice(backward) if pwm else DigitalOutputDevice(backward)
        )

    def on(self, speed=1, t=None, wait=False):


















        if speed > 0:
            self._backward.off()
            self._forward.on(speed, t, wait)

        elif speed < 0:
            self._forward.off()
            self._backward.on(-speed, t, wait)

        else:
            self.off()

    def off(self):



        self._backward.off()
        self._forward.off()

    @property
    def value(self):




        return self._forward.value + (-self._backward.value)

    @value.setter
    def value(self, value):
        if value != 0:
            self.on(value)
        else:
            self.stop()

    def forward(self, speed=1, t=None, wait=False):
















        self.on(speed, t, wait)

    def backward(self, speed=1, t=None, wait=False):
















        self.on(-speed, t, wait)

    def close(self):




        self._forward.close()
        self._backward.close()


Motor.start = Motor.on
Motor.stop = Motor.off


class Robot:






























    def __init__(self, left, right, pwm=True):
        self._left = Motor(left[0], left[1], pwm)
        self._right = Motor(right[0], right[1], pwm)

    @property
    def left_motor(self):



        return self._left

    @property
    def right_motor(self):



        return self._right

    @property
    def value(self):






        return (self._left.value, self._right.value)

    @value.setter
    def value(self, value):
        self._left.value, self._right.value = value

    def forward(self, speed=1, t=None, wait=False):

















        self._left.forward(speed, t, False)
        self._right.forward(speed, t, wait)

    def backward(self, speed=1, t=None, wait=False):

















        self._left.backward(speed, t, False)
        self._right.backward(speed, t, wait)

    def left(self, speed=1, t=None, wait=False):


















        self._left.backward(speed, t, False)
        self._right.forward(speed, t, wait)

    def right(self, speed=1, t=None, wait=False):


















        self._left.forward(speed, t, False)
        self._right.backward(speed, t, wait)

    def stop(self):



        self._left.stop()
        self._right.stop()

    def close(self):




        self._left.close()
        self._right.close()


Rover = Robot


class Stepper(PinsMixin):


























    # Step sequences for different drive modes
    STEP_SEQUENCES = {
        "wave": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        "full": [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]],
        "half": [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1],
        ],
    }

    def __init__(
        self, pins, step_sequence="full", step_delay=0.002, steps_per_rotation=2048
    ):
        if len(pins) != 4:
            raise ValueError("Stepper requires exactly 4 pins")

        self._pin_nums = tuple(pins)
        self._pins = tuple(DigitalOutputDevice(pin) for pin in pins)
        self._step_delay = step_delay
        self._steps_per_rotation = steps_per_rotation
        self._current_step = 0
        self._step_count = 0

        if step_sequence not in self.STEP_SEQUENCES:
            raise ValueError(
                f"Invalid step_sequence. Must be one of: {list(self.STEP_SEQUENCES.keys())}"
            )
        self._step_sequence = step_sequence
        self._sequence = self.STEP_SEQUENCES[step_sequence]

        # Turn off all coils initially
        self._set_step([0, 0, 0, 0])

    def _normalise_direction(self, direction):









        if isinstance(direction, str):
            direction_lower = direction.lower().strip()
            if direction_lower in ("cw", "clockwise"):
                return 1
            elif direction_lower in ("ccw", "counter-clockwise", "counterclockwise"):
                return -1
            else:
                raise ValueError(
                    f"Invalid direction string: '{direction}'. Use 'cw', 'ccw', 'clockwise', or 'counter-clockwise'"
                )
        else:
            # Numeric direction: positive = clockwise, negative = counter-clockwise
            return 1 if direction >= 0 else -1

    def _set_step(self, pattern):

        for pin, state in zip(self._pins, pattern):
            pin.value = state

    def _single_step(self, direction=1):

        normalised_direction = self._normalise_direction(direction)

        if normalised_direction > 0:  # Clockwise
            self._current_step = (self._current_step + 1) % len(self._sequence)
            self._step_count += 1
        else:  # Counter-clockwise
            self._current_step = (self._current_step - 1) % len(self._sequence)
            self._step_count -= 1

        self._set_step(self._sequence[self._current_step])
        sleep(self._step_delay)

    def step(self, steps, direction=1):













        steps = abs(int(steps))

        for _ in range(steps):
            self._single_step(direction)

    def step_to(self, steps, direction):















        target_steps = int(steps)
        current_steps = self._step_count

        normalised_dir = self._normalise_direction(direction)

        if normalised_dir > 0:  # Clockwise - move TO absolute position
            distance = target_steps - current_steps
            if distance > 0:
                self.step(distance, direction)
            elif distance < 0:
                # Wrap around clockwise
                self.step(self._steps_per_rotation + distance, direction)
            # if distance == 0, don't move
        else:  # Counter-clockwise - move BY relative steps
            if target_steps > 0:
                self.step(target_steps, direction)

    def turn(self, angle, direction):











        angle = abs(float(angle))
        steps = int((angle / 360.0) * self._steps_per_rotation)
        self.step(steps, direction)

    def rotate(self, rotations, direction):











        rotations = abs(float(rotations))
        steps = int(rotations * self._steps_per_rotation)
        self.step(steps, direction)

    def turn_to(self, angle, direction):












        # normalise target angle to 0-359 range
        target_angle = abs(float(angle)) % 360.0
        current_angle = self.angle

        # Calculate the shortest path to target angle
        if direction.lower() in ("cw", "clockwise"):
            # Clockwise: calculate distance going clockwise
            if target_angle >= current_angle:
                rotation_angle = target_angle - current_angle
            else:
                rotation_angle = 360.0 - current_angle + target_angle
        else:  # counter-clockwise
            # Counter-clockwise: calculate distance going counter-clockwise
            if target_angle <= current_angle:
                rotation_angle = current_angle - target_angle
            else:
                rotation_angle = current_angle + (360.0 - target_angle)

        # Convert angle to steps and rotate
        steps = int((rotation_angle / 360.0) * self._steps_per_rotation)
        if steps > 0:
            self.step(steps, direction)

    def reset_position(self):

        self._step_count = 0

    def off(self):

        self._set_step([0, 0, 0, 0])

    def set_speed(self, rpm):








        rpm = float(rpm)
        if rpm <= 0:
            raise ValueError("RPM must be positive")

        # Calculate step delay from RPM
        # RPM = rotations per minute
        # steps per rotation = self._steps_per_rotation
        # Total steps per minute = RPM * steps_per_rotation
        # Total steps per second = (RPM * steps_per_rotation) / 60
        # Delay per step = 1 / steps_per_second = 60 / (RPM * steps_per_rotation)
        self._step_delay = 60.0 / (rpm * self._steps_per_rotation)

    def run_continuous(self, seconds=None, direction=1):














        if seconds is None:
            # Run until manually stopped
            try:
                while True:
                    self._single_step(direction)
            except KeyboardInterrupt:
                self.off()
        else:
            # Run for specified duration
            seconds = abs(float(seconds))
            start_time = ticks_ms()
            end_time = start_time + int(seconds * 1000)

            while ticks_ms() < end_time:
                self._single_step(direction)

            self.off()

    @property
    def step_delay(self):

        return self._step_delay

    @step_delay.setter
    def step_delay(self, value):
        self._step_delay = float(value)

    @property
    def step_count(self):

        return self._step_count

    @property
    def angle(self):

        return ((self._step_count / self._steps_per_rotation) * 360.0) % 360.0

    @property
    def steps_per_rotation(self):

        return self._steps_per_rotation

    def close(self):

        self.off()
        for pin in self._pins:
            pin.close()
        self._pins = None


class Servo(PWMOutputDevice):

































    def __init__(
        self,
        pin,
        initial_value=None,
        min_pulse_width=1 / 1000,
        max_pulse_width=2 / 1000,
        frame_width=20 / 1000,
        duty_factor=65535,
    ):
        self._min_duty = int((min_pulse_width / frame_width) * duty_factor)
        self._max_duty = int((max_pulse_width / frame_width) * duty_factor)

        super().__init__(
            pin,
            freq=int(1 / frame_width),
            duty_factor=duty_factor,
            initial_value=initial_value,
        )

    def _state_to_value(self, state):
        return (
            None
            if state == 0
            else clamp(
                (state - self._min_duty) / (self._max_duty - self._min_duty), 0, 1
            )
        )

    def _value_to_state(self, value):
        return (
            0
            if value is None
            else int(self._min_duty + ((self._max_duty - self._min_duty) * value))
        )

    def min(self):



        self.value = 0

    def mid(self):



        self.value = 0.5

    def max(self):



        self.value = 1

    def off(self):



        self.value = None


###############################################################################
# INPUT DEVICES
###############################################################################


class InputDevice:




    def __init__(self, active_state=None):
        self._active_state = active_state

    @property
    def active_state(self):







        return self._active_state

    @active_state.setter
    def active_state(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True

    @property
    def value(self):




        return self._read()


class DigitalInputDevice(InputDevice, PinMixin):
























    def __init__(self, pin, pull_up=False, active_state=None, bounce_time=None):
        super().__init__(active_state)
        self._pin_num = pin
        self._pin = Pin(
            pin, mode=Pin.IN, pull=Pin.PULL_UP if pull_up else Pin.PULL_DOWN
        )
        self._bounce_time = bounce_time
        self._last_callback_ms = (
            None  # Track when we last fired a callback for debouncing
        )

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
        # read the state that triggered the interrupt
        new_state = p.value()

        # did the state actually change from our stored state?
        if self._state != new_state:
            # check if enough time has passed since last callback (debounce)
            current_time_ms = ticks_ms()
            # Use infinity for first event to ensure it always passes the time check.
            # This is mathematically cleaner than checking if _last_callback_ms is None separately.
            time_since_last_callback = (
                current_time_ms - self._last_callback_ms
                if hasattr(self, "_last_callback_ms")
                and self._last_callback_ms is not None
                else float("inf")
            )

            bounce_time = getattr(self, "_bounce_time", None)
            if bounce_time is None or time_since_last_callback >= (bounce_time * 1000):
                # Enough time has passed - update state, fire callback, and record timestamp
                self._state = new_state
                self._last_callback_ms = current_time_ms

                # manage call backs
                callback_to_run = None
                if self.value and self._when_activated is not None:
                    callback_to_run = self._when_activated

                elif not self.value and self._when_deactivated is not None:
                    callback_to_run = self._when_deactivated

                if callback_to_run is not None:

                    def schedule_callback(callback):
                        callback()

                    try:
                        schedule(schedule_callback, callback_to_run)

                    except RuntimeError as e:
                        if str(e) == "schedule queue full":
                            raise EventFailedScheduleQueueFull(
                                "{} - {} not run due to the micropython schedule being full".format(
                                    str(self), callback_to_run.__name__
                                )
                            )
                        else:
                            raise e
            else:
                # Within bounce time - update state to track reality, but suppress callback.
                # Note: _last_callback_ms is intentionally NOT updated here because we want
                # to measure time from the last callback, not the last state change.
                self._state = new_state

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

    @when_deactivated.setter
    def when_deactivated(self, value):
        self._when_deactivated = value

    def close(self):




        self._pin.irq(handler=None)
        self._pin = None


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
Button.is_released = Button.is_inactive
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated


class MotionSensor(DigitalInputDevice):


















    def __init__(self, pin, pull_up=False, bounce_time=1.00):
        super().__init__(pin=pin, pull_up=pull_up, bounce_time=bounce_time)


MotionSensor.motion_detected = MotionSensor.is_active
MotionSensor.motion_not_detected = MotionSensor.is_inactive
MotionSensor.when_motion = MotionSensor.when_activated
MotionSensor.when_no_motion = MotionSensor.when_deactivated


class TouchSensor(Button):



















    def __init__(self, pin, pull_up=False, bounce_time=0.02):
        super().__init__(pin=pin, pull_up=pull_up, bounce_time=bounce_time)


TouchSensor.is_touched = TouchSensor.is_active
TouchSensor.is_not_touched = TouchSensor.is_inactive
TouchSensor.when_touch_starts = TouchSensor.when_activated
TouchSensor.when_touch_ends = TouchSensor.when_deactivated


class AnalogInputDevice(InputDevice, PinMixin):




















    def __init__(self, pin, active_state=True, threshold=0.5):
        self._pin_num = pin
        super().__init__(active_state)
        self._adc = ADC(pin)
        self._threshold = float(threshold)

    def _state_to_value(self, state):
        return (state if self.active_state else 65535 - state) / 65535

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

    def close(self):
        self._adc = None


class Potentiometer(AnalogInputDevice):






















    pass


Pot = Potentiometer


def pico_temp_conversion(voltage):
    # Formula for calculating temp from voltage for the onboard temperature sensor
    return 27 - (voltage - 0.706) / 0.001721


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

    @property
    def conversion(self):



        return self._conversion

    @conversion.setter
    def conversion(self, value):
        self._conversion = value


pico_temp_sensor = TemperatureSensor(4, True, 0.5, pico_temp_conversion)
TempSensor = TemperatureSensor
Thermistor = TemperatureSensor


class DistanceSensor(PinsMixin):















    def __init__(self, echo, trigger, max_distance=1.0):
        self._pin_nums = (echo, trigger)
        self._max_distance = max_distance
        self._echo = Pin(echo, mode=Pin.IN, pull=Pin.PULL_DOWN)
        self._trigger = Pin(trigger, mode=Pin.OUT, value=0)

    def _read(self):
        echo_on = None
        echo_off = None
        timed_out = False

        self._trigger.off()
        sleep(0.000005)
        self._trigger.on()
        sleep(0.00001)
        self._trigger.off()

        # If an echo isn't measured in 100 milliseconds, it should
        # be considered out of range. The maximum length of the
        # echo is 38 milliseconds but it's not known how long the
        # transmission takes after the trigger
        stop = ticks_ms() + 100
        while echo_off is None and not timed_out:
            if self._echo.value() == 1 and echo_on is None:
                echo_on = ticks_us()
            if echo_on is not None and self._echo.value() == 0:
                echo_off = ticks_us()
            if ticks_ms() > stop:
                timed_out = True

        if echo_off is None or timed_out:
            return None
        else:
            distance = ((echo_off - echo_on) * 0.000343) / 2
            distance = min(distance, self._max_distance)
            return distance

    @property
    def value(self):







        distance = self.distance
        return distance / self._max_distance if distance is not None else None

    @property
    def distance(self):




        return self._read()

    @property
    def max_distance(self):



        return self._max_distance
