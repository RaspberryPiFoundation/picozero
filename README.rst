picozero
========

|pypibadge| |docsbadge|

A beginner-friendly library for using common electronics components with the Raspberry Pi Pico.

.. code-block:: python

    from picozero import LED, Button

    led = LED(1)
    button = Button(2)

    button.when_pressed = led.on
    button.when_released = led.off

Status
------

Beta. There will be bugs and issues. API changes are likely. More devices will be added over time.

Documentation
-------------

Documentation is available at `picozero.readthedocs.io <https://picozero.readthedocs.io>`_ :

- `Installation and getting started guide <https://picozero.readthedocs.io/en/latest/gettingstarted.html>`_
- `Recipes and how-to's <https://picozero.readthedocs.io/en/latest/recipes.html>`_
- `API <https://picozero.readthedocs.io/en/latest/api.html>`_

Code
----

The code and project is at `github.com/RaspberryPiFoundation/picozero <https://github.com/RaspberryPiFoundation/picozero>`_. 

Issues can be raised at `github.com/RaspberryPiFoundation/picozero/issues <https://github.com/RaspberryPiFoundation/picozero/issues>`_ (see `contributing <https://picozero.readthedocs.io/en/latest/contributing.html>`_).

The latest distribution is available at `pypi.org/project/picozero/ <https://pypi.org/project/picozero/>`_.

Thanks
------

picozero is inspired by `gpiozero <https://gpiozero.readthedocs.io/en/stable/>`_ (and reuses some of its underlying structure), but is, by design, lighter weight and aligned with the Raspberry Pi Pico. Thank you to everyone who has contributed to the gpiozero project.

.. |pypibadge| image:: https://badge.fury.io/py/picozero.svg
   :target: https://badge.fury.io/py/picozero
   :alt: Latest Version

.. |docsbadge| image:: https://readthedocs.org/projects/picozero/badge/
   :target: https://readthedocs.org/projects/picozero/
   :alt: Docs
