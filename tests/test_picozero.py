from picozero import *
from time import ticks_ms

def log_device_values(d, timeout):
    values = [d.value]
    
    timeout_ms = ticks_ms() + (timeout * 1000)
    
    while ticks_ms() < timeout_ms:
        if values[-1] != d.value:
            values.append(d.value)
            
    return values

def test_digital_output_device_default_values():
    d = DigitalOutputDevice(1)
    
    assert d.active_high == True
    assert d.value == 0
    assert d.is_active == False
    
    d.on()
    assert d.value == True
    assert d._pin.value() == 1
    assert d.is_active == True
    
    d.off()
    assert d.value == False
    assert d._pin.value() == 0
    assert d.is_active == False
    
    d.value = True
    assert d.value == 1
    d.value = False
    assert d.value == 0
    
    d.close()
    assert d._pin == None
    
def test_digital_output_device_alt_values():
    d = DigitalOutputDevice(1, active_high=False, initial_value=True)
    
    assert d.active_high == False
    assert d.value == True
    
    d.off()
    assert d._pin.value() == 1
    
    d.on()
    assert d._pin.value() == 0
    
    d.close()
    
def test_digital_output_device_blink():
    d = DigitalOutputDevice(1)
    
    d.blink()
    values = log_device_values(d, 1.1)
    assert values == [1,0]
    d.off()
    assert d.value == False
    
    d.blink(on_time=0.1, off_time=0.1, n=2)
    values = log_device_values(d, 0.5)
    assert values == [1,0,1,0]
    assert d.value == False

    d.close()

def test_digital_LED():
    d = DigitalLED(1)
    assert d.is_lit == False
    d.close()

def test_pwm_output_device_default_values():
    d = PWMOutputDevice(1)
    
    assert d.active_high == True
    assert d.value == 0
    assert d.is_active == False
    assert d.freq == 100
    
    d.on()
    assert d.value == True
    assert d.is_active == True
    assert d._pwm.duty_u16() == 65535
    assert d.is_active == True
    
    d.off()
    assert d.value == False
    assert d._pwm.duty_u16() == 0
    assert d.is_active == False
    
    d.value = True
    assert d.value == 1
    d.value = False
    assert d.value == 0
    
    d.value = 0.5
    assert round(d.value, 2) == 0.5
    assert d.is_active == True
    
    d.close()
    assert d._pwm == None
    
def test_pwm_output_device_alt_values():
    d = PWMOutputDevice(1, freq=200, duty_factor=10000, active_high=False, initial_value=True)
    
    assert d.active_high == False
    assert d.value == True
    assert d.freq == 200
    
    d.off()
    # pwm returns 1 less than the duty_factor unless the duty is set to the maximum 65535
    assert d._pwm.duty_u16() == 9999
    assert round(d.value, 2) == 0
    
    d.on()
    assert d._pwm.duty_u16() == 0
    assert d.value == 1
    
    d.off()
    
    d.close()

def test_LED_factory():
    d = LED(1)
    assert isinstance(d, PWMLED)
    d.close()
    
    d = LED(1, use_pwm=False)
    assert isinstance(d, DigitalLED)
    d.close()

