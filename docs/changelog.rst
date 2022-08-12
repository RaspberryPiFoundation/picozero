Change log
==========

.. currentmodule:: picozero

0.3.0 - 2022-08-12
~~~~~~~~~~~~~~~~~~

+ Introduced ``Motor``, ``Robot`` and ``DistanceSensor`` classes.
+ Renamed ``LED`` factory ``use_pwm`` parameter to ``pwm`` to match other classes. Note - this is an API breaking change. 
+ Resolved issue with ``RGBLED`` when not using ``pwm``.
+ Resolved issue where ``blink`` / ``pulse`` rates of ``0`` raised a traceback error.
+ Other minor bug fixes
+ Documentation updates

0.2.0 - 2022-06-29
~~~~~~~~~~~~~~~~~~

+ Pico W compatibility fix for onboard LED

0.1.1 - 2022-06-08
~~~~~~~~~~~~~~~~~~

+ Minor bug fixes found during testing
+ Small improvements to exception messages
+ Added close methods to Speaker and PWMOutputDevice
+ Added unit tests
+ Added RGBLED.colour as an alias to RGBLED.color

0.1.0 - 2022-04-08
~~~~~~~~~~~~~~~~~~

+ Beta release
+ Documentation update
+ Minor bug fixes and refactoring

0.0.2 - 2022-03-31
~~~~~~~~~~~~~~~~~~

+ Bug fixes and documentation updates

0.0.1 - 2022-03-21
~~~~~~~~~~~~~~~~~~

+ Initial alpha release to test installation process

