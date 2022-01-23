Recipes
=======

The recipes provide examples of how you can use picozero.

Importing Pico Zero
-------------------

.. currentmodule:: picozero

You will need add an `import` line to the top of your script to use Pico Zero.

You can import just what you need, separating items with a comma `,`::

    from picozero import pico_led, LED

Now you can use :obj:`~picozero.pico_led` and :class:`~picozero.LED` in your script::

    pico_led.on() # Turn on the LED on the Raspberry Pi Pico
    led = LED(14) # Control an LED connected to pin GP14 
    led.on()

Alternatively, the whole Pico Zero library can be imported::

    import picozero

In this case, all references to Pico Zero items must be prefixed::

    picozero.pico_led.on()
    led = picozero.LED(14)


Pico LED
--------

.. image:: images/pico_led.svg
    :alt: A diagram of the Raspberry Pi Pico with a GP25 label attached to the onboard LED

To turn on the LED on Raspberry Pi Pico:

.. literalinclude:: examples/pico_led.py

Run your script to see the LED turn on.

Using the :obj:`pico_led` is equivalent to::

    pico_led = LED(25) 

You can use :obj:`pico_led` in the same way as external LEDs created using :class:`LED`.

LED
------
 
LEDs are simple components.

Flash
~~~~~

.. literalinclude:: examples/led_on_off.py

Alternatively, you can use the :meth:`~picozero.LED.blink` method.

.. literalinclude:: examples/led_blink.py
