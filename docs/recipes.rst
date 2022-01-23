Recipes
=======

The recipes provide examples of how you can use picozero.

Importing Pico Zero
-------------------

.. currentmodule:: picozero

To use the :obj:`pico_led`, import it at the top of your script::

    from picozero import pico_led

Now you can program the small LED on the Raspberry Pi Pico::

    pico_led.on()

Run your script to see the LED turn on.

.. image:: images/pico_led.svg
    :alt: A diagram of the Raspberry Pi Pico with a GP25 label attached to the onboard LED


LED
------
 
LEDs are simple components.

Flash
~~~~~

.. literalinclude:: examples/led_on_off.py

Alternatively, you can use the :meth:`~picozero.LED.blink` method.

.. literalinclude:: examples/led_blink.py
