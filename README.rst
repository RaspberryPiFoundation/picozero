picozero
========

|pypibadge| |docsbadge|

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

Status
------

Beta. There will be bugs and issues. API changes are likely.

Documentation is available at `picozero.readthedocs.io <https://picozero.readthedocs.io>`_ :

- `Installation and getting started guide <https://picozero.readthedocs.io/en/latest/gettingstarted.html>`_
- `Recipes and how-to's <https://picozero.readthedocs.io/en/latest/recipes.html>`_
- `API <https://picozero.readthedocs.io/en/latest/api.html>`_

Notes
-----

picozero is inspired by `gpiozero <https://gpiozero.readthedocs.io/en/stable/>`_ (and reuses some of its underlying structure), but is by design lighter weight and aligned with the Raspberry Pi Pico. Thank you to everyone who has contributed to the gpiozero project.

.. |pypibadge| image:: https://badge.fury.io/py/picozero.svg
   :target: https://badge.fury.io/py/picozero
   :alt: Latest Version

.. |docsbadge| image:: https://readthedocs.org/projects/picozero/badge/
   :target: https://readthedocs.org/projects/picozero/
   :alt: Docs
