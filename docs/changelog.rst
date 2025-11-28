Change log
==========

.. currentmodule:: picozero

0.6.0 - 2025-11-26
-----------

+ Introduced ``Stepper`` class for stepper motors

0.5.2 - 2025-11-26
-----------

+ Fixed 404 in manual install instructions

0.5.1 - 2025-11-24
-----------

+ Fix to incorrect example in documentation

0.5.0 - 2025-10-31
-----------

+ Introduced ``MotionSensor`` class for PIR sensors

0.4.2 - 2023-05-12
------------------

+ Bug fix relating to DigitalInputDevice bounce times
+ Updated tests after a change in micropython 1.20+

0.4.1 - 2022-12-22
------------------

+ Introduced ``pinout()``
+ Bug fix with ``DigitalInputDevice.when_deactivated`` decorator
+ Documentation tidy up and minor fixes

0.4.0 - 2022-11-18
------------------

+ Introduced ``Servo`` class
+ Documentation fixes

0.3.0 - 2022-08-12
------------------

+ Introduced ``Motor``, ``Robot``, and ``DistanceSensor`` classes.
+ Renamed ``LED`` factory ``use_pwm`` parameter to ``pwm`` to match other classes. **Note:** This is an API breaking change. 
+ Resolved issue with ``RGBLED`` when not using ``pwm``.
+ Resolved issue where ``blink`` / ``pulse`` rates of ``0`` raised a traceback error.
+ Other minor bug fixes.
+ Documentation updates.

0.2.0 - 2022-06-29
------------------

+ Pico W compatibility fix for onboard LED.

0.1.1 - 2022-06-08
------------------

+ Minor fixes for bugs found during testing.
+ Small improvements to exception messages.
+ Added close methods to Speaker and PWMOutputDevice.
+ Added unit tests.
+ Added RGBLED.colour as an alias to RGBLED.color.

0.1.0 - 2022-04-08
------------------

+ Beta release.
+ Documentation updates.
+ Minor bug fixes and refactoring.

0.0.2 - 2022-03-31
------------------

+ Bug fixes and documentation updates.

0.0.1 - 2022-03-21
------------------

+ Initial alpha release to test installation process.

