import unittest
from picozero import *
from time import ticks_ms


def log_device_values(d, timeout):
    values = [d.value]

    timeout_ms = ticks_ms() + (timeout * 1000)

    while ticks_ms() < timeout_ms:
        if values[-1] != d.value:
            values.append(d.value)

    return values


class MockPin:
    def __init__(self, initial_state=0, irq_handler=None):
        self._state = initial_state
        self._irq_handler = irq_handler

    def read(self):
        return self._state

    def write(self, state):
        self._state = state
        if self._irq_handler is not None:
            self._irq_handler(self)

    def value(self, state=None):
        if state is None:
            return self._state
        else:
            self.write(state)

    def irq(self, handler, args=None):
        self._irq_handler = handler


class MockADC:
    def __init__(self, initial_state=0):
        self._state = initial_state

    def read(self):
        return self._state

    def write(self, state):
        self._state = state

    def read_u16(self):
        return self._state


class MockEvent:
    def __init__(self):
        self._is_set = False

    def set(self):
        self._is_set = True

    def is_set(self):
        return self._is_set

    def reset(self):
        self._is_set = False


class Testpicozero(unittest.TestCase):

    def assertInRange(self, value, lower, upper):
        msg = "Expected %r to be in range {} to {}".format(lower, upper)
        self.assertTrue(value <= upper, msg)
        self.assertTrue(value >= lower, msg)

    ###########################################################################
    # SUPPORTING
    ###########################################################################

    def test_pinout(self):
        pins = pinout(output=False)
        self.assertIsNotNone(pins)

    ###########################################################################
    # OUTPUT DEVICES
    ###########################################################################

    def test_digital_output_device_default_values(self):
        d = DigitalOutputDevice(1)

        self.assertTrue(d.active_high)
        self.assertEqual(d.value, 0)
        self.assertFalse(d.is_active)

        d.on()
        self.assertTrue(d.value)
        self.assertEqual(d._pin.value(), 1)
        self.assertTrue(d.is_active)

        d.off()
        self.assertFalse(d.value)
        self.assertEqual(d._pin.value(), 0)
        self.assertFalse(d.is_active)

        d.value = True
        self.assertEqual(d.value, 1)
        d.value = False
        self.assertEqual(d.value, 0)

        d.close()
        self.assertIsNone(d._pin)

    def test_digital_output_device_alt_values(self):
        d = DigitalOutputDevice(1, active_high=False, initial_value=True)

        self.assertFalse(d.active_high)
        self.assertTrue(d.value)

        d.off()
        self.assertEqual(d._pin.value(), 1)

        d.on()
        self.assertEqual(d._pin.value(), 0)

        d.close()

    def test_digital_output_device_blink(self):
        d = DigitalOutputDevice(1)

        d.blink()
        values = log_device_values(d, 1.1)
        self.assertEqual(values, [1, 0])
        d.off()
        self.assertFalse(d.value)

        d.blink(on_time=0.1, off_time=0.1, n=2)
        values = log_device_values(d, 0.5)
        self.assertEqual(values, [1, 0, 1, 0])
        self.assertFalse(d.value)

        d.close()

    def test_digital_LED(self):
        d = DigitalLED(1)
        self.assertFalse(d.is_lit)
        d.close()

    def test_pwm_output_device_default_values(self):
        d = PWMOutputDevice(1)

        self.assertTrue(d.active_high)
        self.assertEqual(d.value, 0)
        self.assertFalse(d.is_active)
        self.assertEqual(d.freq, 100)

        d.on()
        self.assertTrue(d.value)
        self.assertTrue(d.is_active)
        self.assertEqual(d._pwm.duty_u16(), 65535)
        self.assertTrue(d.is_active)

        d.off()
        self.assertFalse(d.value)
        self.assertEqual(d._pwm.duty_u16(), 0)
        self.assertFalse(d.is_active)

        d.value = True
        self.assertEqual(d.value, 1)
        d.value = False
        self.assertEqual(d.value, 0)

        d.value = 0.5
        self.assertAlmostEqual(d.value, 0.5, places=2)
        self.assertTrue(d.is_active)

        d.close()
        self.assertIsNone(d._pwm)

    def test_pwm_output_device_alt_values(self):
        d = PWMOutputDevice(
            1, freq=200, duty_factor=10000, active_high=False, initial_value=True
        )

        self.assertFalse(d.active_high)
        self.assertTrue(d.value)
        self.assertEqual(d.freq, 200)

        d.off()
        # prior to micropython v1.20 PWM returned 1 less than the duty_factor
        # unless the duty was set to the maximum 65535
        # self.assertEqual(d._pwm.duty_u16(), 9999)
        self.assertEqual(d._pwm.duty_u16(), 10000)
        self.assertAlmostEqual(d.value, 0, places=2)

        d.on()
        self.assertEqual(d._pwm.duty_u16(), 0)
        self.assertEqual(d.value, 1)

        d.off()

        d.close()

    def test_pwm_output_device_blink(self):
        d = PWMOutputDevice(1)

        d.blink()
        values = log_device_values(d, 1.1)
        self.assertEqual(values, [1, 0])
        d.off()
        self.assertFalse(d.value)

        d.blink(on_time=0.1, off_time=0.1, n=2)
        values = log_device_values(d, 0.5)
        self.assertEqual(values, [1, 0, 1, 0])
        self.assertFalse(d.value)

        d.close()

    def test_pwm_output_device_pulse(self):
        d = PWMOutputDevice(1)

        d.pulse(n=1)
        values = log_device_values(d, 2.1)

        expected = [
            0.0,
            0.04,
            0.08,
            0.12,
            0.16,
            0.2,
            0.24,
            0.28,
            0.32,
            0.36,
            0.4,
            0.44,
            0.48,
            0.52,
            0.56,
            0.6,
            0.64,
            0.68,
            0.72,
            0.76,
            0.8,
            0.84,
            0.88,
            0.92,
            0.96,
            1.0,
            0.96,
            0.92,
            0.88,
            0.84,
            0.8,
            0.76,
            0.72,
            0.68,
            0.64,
            0.6,
            0.56,
            0.52,
            0.48,
            0.44,
            0.4,
            0.36,
            0.32,
            0.28,
            0.24,
            0.2,
            0.16,
            0.12,
            0.08,
            0.04,
            0.0,
        ]

        if len(values) == len(expected):
            for i in range(len(values)):
                self.assertAlmostEqual(values[i], expected[i], places=2)
        else:
            self.fail(f"{len(values)} were generated, {len(expected)} were expected.")

        d.pulse(fade_in_time=0.5, fade_out_time=1, n=1, fps=4)
        values = log_device_values(d, 2.1)

        expected = [0.0, 0.5, 1.0, 0.75, 0.5, 0.25, 0]

        if len(values) == len(expected):
            for i in range(len(values)):
                self.assertAlmostEqual(values[i], expected[i], places=2)
        else:
            self.fail(
                f"{len(values)} values were generated, {len(expected)} were expected."
            )

        d.close()

    def test_motor_default_values(self):
        d = Motor(1, 2)

        self.assertEqual(d.value, 0)

        d.on()
        self.assertEqual(d.value, 1)

        d.stop()
        self.assertEqual(d.value, 0)

        d.forward()
        self.assertEqual(d.value, 1)

        d.backward()
        self.assertEqual(d.value, -1)

        d.value = 0.5
        self.assertAlmostEqual(d.value, 0.5, places=2)

        d.value = -0.5
        self.assertAlmostEqual(d.value, -0.5, places=2)

        d.forward(1, t=0.5)
        values = log_device_values(d, 0.6)
        self.assertEqual(values, [1, 0])
        self.assertEqual(d.value, 0)

        d.backward(1, t=0.5)
        values = log_device_values(d, 0.6)
        self.assertEqual(values, [-1, 0])
        self.assertEqual(d.value, 0)

        d.close()

    def test_motor_alt_values(self):
        d = Motor(1, 2, pwm=False)

        d.value = 0.5
        self.assertEqual(d.value, 1)

        d.value = -0.5
        self.assertEqual(d.value, -1)

        d.value = 0
        self.assertEqual(d.value, 0)

        d.close()

    def test_robot(self):
        d = Robot(left=(1, 2), right=(3, 4))

        d.forward()
        self.assertEqual(d.value, (1, 1))

        d.left()
        self.assertEqual(d.value, (-1, 1))

        d.right()
        self.assertEqual(d.value, (1, -1))

        d.value = (0.5, -0.5)
        self.assertAlmostEqual(d.left_motor.value, 0.5, places=2)
        self.assertAlmostEqual(d.right_motor.value, -0.5, places=2)

        d.stop()
        self.assertEqual(d.value, (0, 0))

        d.close()

    def test_LED_factory(self):
        d = LED(1)
        self.assertIsInstance(d, PWMLED)
        d.close()

        d = LED(1, pwm=False)
        self.assertIsInstance(d, DigitalLED)
        d.close()

    def test_pico_led(self):

        self.assertIsInstance(pico_led, DigitalLED)

        self.assertEqual(pico_led.value, 0)

        pico_led.on()
        self.assertEqual(pico_led.value, 1)

        pico_led.off()
        self.assertEqual(pico_led.value, 0)

    def test_rgb_led_default_values(self):
        d = RGBLED(1, 2, 3)

        self.assertEqual(d.value, (0, 0, 0))

        d.on()
        self.assertEqual(d.value, (1, 1, 1))

        d.off()
        self.assertEqual(d.value, (0, 0, 0))

        d.value = (0.25, 0.5, 0.75)
        self.assertAlmostEqual(d.value[0], 0.25, places=2)
        self.assertAlmostEqual(d.value[1], 0.5, places=2)
        self.assertAlmostEqual(d.value[2], 0.75, places=2)

        d.red = 200
        self.assertAlmostEqual(d.value[0], 0.78, places=2)

        d.green = 100
        self.assertAlmostEqual(d.value[1], 0.39, places=2)

        d.blue = 50
        self.assertAlmostEqual(d.value[2], 0.20, places=2)

        d.close()

    def test_rgb_led_alt_values(self):
        d = RGBLED(1, 2, 3, initial_value=(1, 1, 1), pwm=False)

        self.assertEqual(d.value, (1, 1, 1))

        d.on()
        self.assertEqual(d.value, (1, 1, 1))

        d.off()
        self.assertEqual(d.value, (0, 0, 0))

        d.value = (1, 1, 1)
        self.assertEqual(d.value, (1, 1, 1))

        d.value = (0, 0.5, 1)
        self.assertEqual(d.value, (0, 1, 1))

        d.close()

    def test_servo_default_value(self):
        d = Servo(1)

        self.assertEqual(d.value, None)

        d.value = 0
        self.assertAlmostEqual(d.value, 0, 2)
        self.assertInRange(
            d._pwm.duty_u16(),
            int((0.001 / 0.02) * 65535) - 1,
            int((0.001 / 0.02) * 65535) + 1,
        )

        d.value = 1
        self.assertAlmostEqual(d.value, 1, 2)
        self.assertInRange(
            d._pwm.duty_u16(),
            int((0.002 / 0.02) * 65535) - 1,
            int((0.002 / 0.02) * 65535) + 1,
        )

        d.value = None
        self.assertEqual(d.value, None)
        self.assertEqual(d._pwm.duty_u16(), 0)

        d.min()
        self.assertAlmostEqual(d.value, 0, 2)

        d.mid()
        self.assertAlmostEqual(d.value, 0.5, 2)

        d.max()
        self.assertAlmostEqual(d.value, 1, 2)

        d.off()
        self.assertEqual(d._pwm.duty_u16(), 0)

        d.close()

    def test_servo_alt_values(self):
        d = Servo(
            1,
            initial_value=1,
            min_pulse_width=0.9 / 1000,
            max_pulse_width=2.1 / 1000,
            frame_width=19 / 1000,
        )

        self.assertAlmostEqual(d.value, 1, 2)

        d.value = 0
        self.assertInRange(
            d._pwm.duty_u16(),
            int((0.0009 / 0.019) * 65535) - 1,
            int((0.0009 / 0.019) * 65535) + 1,
        )

        d.value = 1
        self.assertInRange(
            d._pwm.duty_u16(),
            int((0.0021 / 0.019) * 65535) - 1,
            int((0.0021 / 0.019) * 65535) + 1,
        )

        d.value = None
        self.assertEqual(d._pwm.duty_u16(), 0)

        d.close()

    ###########################################################################
    # INPUT DEVICES
    ###########################################################################

    def test_digital_input_device_default_values(self):
        d = DigitalInputDevice(1)

        pin = MockPin(irq_handler=d._pin_change)
        d._pin = pin

        self.assertTrue(d.active_state)
        self.assertFalse(d.is_active)
        self.assertEqual(d.value, 0)

        pin.write(1)

        self.assertTrue(d.is_active)
        self.assertEqual(d.value, 1)

        pin.write(0)

        self.assertFalse(d.is_active)
        self.assertEqual(d.value, 0)

        d.close()

    def test_digital_input_device_alt_values(self):
        d = DigitalInputDevice(1, pull_up=False, active_state=False)

        pin = MockPin(irq_handler=d._pin_change)
        d._pin = pin

        self.assertFalse(d.active_state)
        self.assertTrue(d.is_active)
        self.assertEqual(d.value, 1)

        pin.write(1)

        self.assertFalse(d.is_active)
        self.assertEqual(d.value, 0)

        pin.write(0)

        self.assertTrue(d.is_active)
        self.assertEqual(d.value, 1)

        d.close()

    def test_digital_input_device_activated_deactivated(self):
        d = DigitalInputDevice(1)

        pin = MockPin(irq_handler=d._pin_change)
        d._pin = pin

        event_activated = MockEvent()
        event_deactivated = MockEvent()

        d.when_activated = event_activated.set
        d.when_deactivated = event_deactivated.set

        self.assertFalse(event_activated.is_set())
        pin.write(1)
        self.assertTrue(event_activated.is_set())

        self.assertFalse(event_deactivated.is_set())
        pin.write(0)
        self.assertTrue(event_deactivated.is_set())

        d.close()

    def test_adc_input_device_default_values(self):
        d = AnalogInputDevice(1)

        adc = MockADC()
        d._adc = adc

        self.assertTrue(d.active_state)
        self.assertFalse(d.is_active)
        self.assertEqual(d.value, 0)

        adc.write(65535)
        self.assertTrue(d.is_active)
        self.assertEqual(d.value, 1)
        self.assertEqual(d.voltage, 3.3)

        adc.write(0)
        self.assertFalse(d.is_active)
        self.assertEqual(d.value, 0)
        self.assertEqual(d.voltage, 0)

        # mid point
        adc.write(32767)
        self.assertAlmostEqual(d.value, 0.5, places=2)
        self.assertAlmostEqual(d.voltage, 1.65, places=2)

        d.close()

    def test_adc_input_device_alt_values(self):
        d = AnalogInputDevice(1, active_state=False, threshold=0.1)

        adc = MockADC()
        d._adc = adc

        self.assertFalse(d.active_state)
        self.assertTrue(d.is_active)
        self.assertEqual(d.value, 1)

        adc.write(65535)
        self.assertFalse(d.is_active)
        self.assertEqual(d.value, 0)
        self.assertEqual(d.voltage, 0)

        adc.write(0)
        self.assertTrue(d.is_active)
        self.assertEqual(d.value, 1)
        self.assertEqual(d.voltage, 3.3)

        d.close()

    def test_adc_input_device_threshold(self):
        d = AnalogInputDevice(1)

        adc = MockADC()
        d._adc = adc

        self.assertFalse(d.is_active)

        # mid point
        adc.write(32767)
        self.assertFalse(d.is_active)

        # above threshold
        adc.write(32768)
        self.assertTrue(d.is_active)

        # below threshold
        adc.write(32766)
        self.assertFalse(d.is_active)

        d.threshold = 0.1

        self.assertTrue(d.is_active)

        adc.write(6553)
        self.assertFalse(d.is_active)

        d.close()

    def test_temp_sensory(self):

        def temp_conversion(voltage):
            return voltage + 2

        t = TemperatureSensor(4, conversion=temp_conversion)

        adc = MockADC()
        t._adc = adc

        adc.write(65535)
        self.assertEqual(t.temp, 3.3 + 2)

        adc.write(0)
        self.assertEqual(t.temp, 2)

        t.close()

    def test_pico_temp_sensor(self):

        self.assertIsInstance(pico_temp_sensor, TemperatureSensor)
        self.assertEqual(pico_temp_sensor.pin, 4)
        self.assertIsNotNone(pico_temp_sensor.temp)

    def test_stepper_basic_configuration(self):
        """
        Test 1: Basic stepper motor initialization and configuration.
        """
        stepper = Stepper((1, 2, 3, 4))

        # Test initial configuration
        self.assertEqual(stepper.pins, (1, 2, 3, 4))
        self.assertEqual(stepper.step_count, 0)
        self.assertEqual(stepper.angle, 0.0)
        self.assertEqual(stepper.steps_per_revolution, 2048)
        self.assertEqual(stepper.step_delay, 0.002)

        # Test invalid pin count
        with self.assertRaises(ValueError):
            Stepper((1, 2, 3))  # Too few pins

        # Test invalid step sequence
        with self.assertRaises(ValueError):
            Stepper((1, 2, 3, 4), step_sequence="invalid")

        stepper.close()

    def test_stepper_simple_methods(self):
        """
        Test 2: Simple single-parameter methods (convenience methods).
        """
        stepper = Stepper((1, 2, 3, 4))

        # Test default direction (should be clockwise)
        initial_count = stepper.step_count
        stepper.step(10)  # Default direction
        self.assertEqual(stepper.step_count, initial_count + 10)

        # Test convenience methods - clockwise
        stepper.step_clockwise(5)
        self.assertEqual(stepper.step_count, initial_count + 15)

        # Test convenience methods - counter-clockwise
        stepper.step_counterclockwise(3)
        self.assertEqual(stepper.step_count, initial_count + 12)

        # Test short aliases
        stepper.step_cw(2)
        self.assertEqual(stepper.step_count, initial_count + 14)

        stepper.step_ccw(4)
        self.assertEqual(stepper.step_count, initial_count + 10)

        stepper.close()

    def test_stepper_parameterized_methods(self):
        """
        Test 3: Parameterized methods with flexible direction handling.
        """
        stepper = Stepper((1, 2, 3, 4))
        initial_count = stepper.step_count

        # Test numeric directions
        stepper.step(10, direction=1)  # Clockwise
        self.assertEqual(stepper.step_count, initial_count + 10)

        stepper.step(5, direction=-1)  # Counter-clockwise
        self.assertEqual(stepper.step_count, initial_count + 5)

        # Test string directions
        stepper.step(8, direction="cw")
        self.assertEqual(stepper.step_count, initial_count + 13)

        stepper.step(3, direction="ccw")
        self.assertEqual(stepper.step_count, initial_count + 10)

        # Test full string directions
        stepper.step(5, direction="clockwise")
        self.assertEqual(stepper.step_count, initial_count + 15)

        stepper.step(7, direction="counter-clockwise")
        self.assertEqual(stepper.step_count, initial_count + 8)

        # Test invalid direction
        with self.assertRaises(ValueError):
            stepper.step(5, direction="invalid")

        stepper.close()

    def test_stepper_angle_and_revolution_methods(self):
        """
        Test 4: Higher-level methods (angle-based and revolution-based).
        """
        stepper = Stepper(
            (1, 2, 3, 4), steps_per_revolution=200
        )  # Use smaller value for testing

        # Test angle calculations
        initial_angle = stepper.angle
        stepper.rotate(90, direction=1)
        expected_steps = int((90 / 360.0) * 200)
        self.assertEqual(stepper.step_count, expected_steps)
        self.assertAlmostEqual(stepper.angle, 90.0, places=1)

        # Test revolution methods
        stepper.reset_position()
        stepper.revolution(0.5, direction=1)  # Half revolution
        self.assertEqual(stepper.step_count, 100)
        self.assertAlmostEqual(stepper.angle, 180.0, places=1)

        # Test revolve alias
        stepper.reset_position()
        stepper.revolve(1, direction=1)  # Full revolution
        self.assertEqual(stepper.step_count, 200)
        self.assertAlmostEqual(stepper.angle, 360.0, places=1)

        stepper.close()

    def test_stepper_advanced_features(self):
        """
        Test 5: Advanced features (position tracking, sequences, etc.).
        """
        stepper = Stepper((1, 2, 3, 4), step_sequence="half", steps_per_revolution=100)

        # Test different step sequences
        self.assertEqual(len(stepper.STEP_SEQUENCES["half"]), 8)
        self.assertEqual(len(stepper.STEP_SEQUENCES["full"]), 4)
        self.assertEqual(len(stepper.STEP_SEQUENCES["wave"]), 4)

        # Test position tracking through multiple movements
        stepper.step_clockwise(25)
        stepper.step_counterclockwise(10)
        stepper.rotate_clockwise(90)

        expected_angle_steps = int((90 / 360.0) * 100)
        expected_total = 25 - 10 + expected_angle_steps
        self.assertEqual(stepper.step_count, expected_total)

        # Test position reset
        stepper.reset_position()
        self.assertEqual(stepper.step_count, 0)
        self.assertEqual(stepper.angle, 0.0)

        # Test speed control
        original_delay = stepper.step_delay
        stepper.step_delay = 0.001
        self.assertEqual(stepper.step_delay, 0.001)
        stepper.step_delay = original_delay

        stepper.close()


unittest.main()
