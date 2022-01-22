Recipes
=======

The recipes provide examples of how you can use picozero.

Importing Pico Zero
-------------------

.. image:: images/pico_led.*
    :alt: A diagram of the Raspberry Pi Pico with a GP25 label attached to the onboard LED


LED
------

LEDs are simple components.

Flash
~~~~~

.. currentmodule:: picozero

.. literalinclude:: examples/led_on_off.py

Alternatively, you can use the :meth:`~picozero.LED.blink` method.

.. literalinclude:: examples/led_blink.py
