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
        self.assertEqual(values, [1,0])
        d.off()
        self.assertFalse(d.value)
        
        d.blink(on_time=0.1, off_time=0.1, n=2)
        values = log_device_values(d, 0.5)
        self.assertEqual(values, [1,0,1,0])
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
        self.assertEqual(d._pwm.duty_u16(),0)
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
        d = PWMOutputDevice(1, freq=200, duty_factor=10000, active_high=False, initial_value=True)
        
        self.assertFalse(d.active_high)
        self.assertTrue(d.value)
        self.assertEqual(d.freq, 200)
        
        d.off()
        # pwm returns 1 less than the duty_factor unless the duty is set to the maximum 65535
        self.assertEqual(d._pwm.duty_u16(), 9999)
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
        self.assertEqual(values, [1,0])
        d.off()
        self.assertFalse(d.value)
        
        d.blink(on_time=0.1, off_time=0.1, n=2)
        values = log_device_values(d, 0.5)
        self.assertEqual(values, [1,0,1,0])
        self.assertFalse(d.value)

        d.close()
        
    def test_pwm_output_device_pulse(self):
        d = PWMOutputDevice(1)
        
        d.pulse(n=1)
        values = log_device_values(d, 2.1)
        
        expected = [
            0.0, 0.04, 0.08, 0.12, 0.16, 0.2, 0.24, 0.28, 0.32, 0.36, 0.4,
            0.44, 0.48, 0.52, 0.56, 0.6, 0.64, 0.68, 0.72, 0.76, 0.8, 0.84,
            0.88, 0.92, 0.96, 1.0, 0.96, 0.92, 0.88, 0.84, 0.8, 0.76,
            0.72, 0.68, 0.64, 0.6, 0.56, 0.52, 0.48, 0.44, 0.4, 0.36, 0.32,
            0.28, 0.24, 0.2, 0.16, 0.12, 0.08, 0.04, 0.0]
        
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
            self.fail(f"{len(values)} values were generated, {len(expected)} were expected.")
        
        d.close()

    def test_LED_factory(self):
        d = LED(1)
        self.assertIsInstance(d, PWMLED)
        d.close()
        
        d = LED(1, use_pwm=False)
        self.assertIsInstance(d, DigitalLED)
        d.close()
        
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
        

unittest.main()
