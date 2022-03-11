picozero
========

A beginner-friendly library for using common electronics components with the Raspberry Pi Pico.

.. code-block:: python

    from picozero import LED, Button

    led = LED(1)
    button = Button(2)

    while True:
        if button.is_pressed:
            led.on()
        else:
            led.off() 

Full documentation is available at `picozero.readthedocs.io <https://picozero.readthedocs.io>`_ :

- `Installation and getting started guide <https://picozero.readthedocs.io/en/latest/gettingstarted.html>`_
- `Recipes and how-to's <https://picozero.readthedocs.io/en/latest/recipes.html>`_
- `API <https://picozero.readthedocs.io/en/latest/api.html>`_

picozero is inspired by `gpiozero <https://gpiozero.readthedocs.io/en/stable/>`_ (and reuses some of its underlying structure), but is by design lighter weight and aligned with the Raspberry Pi Pico. 

