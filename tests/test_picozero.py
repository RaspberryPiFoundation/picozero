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

    def test_LED_factory(self):
        d = LED(1)
        self.assertIsInstance(d, PWMLED)
        d.close()
        
        d = LED(1, use_pwm=False)
        self.assertIsInstance(d, DigitalLED)
        d.close()

unittest.main()
