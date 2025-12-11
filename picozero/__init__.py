__name__ = "picozero"
__package__ = "picozero"
__version__ = "0.7.0"
__author__ = "Raspberry Pi Foundation"

from .picozero import (
    PWMChannelAlreadyInUse,
    EventFailedScheduleQueueFull,
    pinout,
    DigitalOutputDevice,
    DigitalLED,
    Buzzer,
    PWMOutputDevice,
    PWMLED,
    LED,
    pico_led,
    PWMBuzzer,
    Speaker,
    RGBLED,
    Motor,
    Robot,
    Stepper,
    Servo,
    DigitalInputDevice,
    Switch,
    Button,
    MotionSensor,
    TouchSensor,
    AnalogInputDevice,
    Potentiometer,
    Pot,
    TemperatureSensor,
    pico_temp_sensor,
    TempSensor,
    Thermistor,
    DistanceSensor,
)

# WiFi is only available on Pico W, so import it from a separate module to avoid
# memory issues on regular Pico
try:
    from .wifi import WiFi
except ImportError:
    pass
