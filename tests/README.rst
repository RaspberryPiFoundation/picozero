Tests
=====

The tests are design to be run on a Raspberry Pi Pico.

Setup
-----

1. Install the `picozero <https://pypi.org/project/picozero/>`_ package.
2. Install the `micropython-unittest <https://pypi.org/project/micropython-unittest/>`_ package.
3. Copy the ``test_picozero.py`` to the pico.
4. Run the ``test_picozero.py`` file.

Error messsages
---------------

If a test fails it is helpful to be able to see verbose error messages. To see error messages you need to modify the ``lib/unittest.py`` file on the pico.

Locate the following code in the ``run_class`` function::

    # Uncomment to investigate failure in detail
    #raise

Uncomment ``raise``::

    # Uncomment to investigate failure in detail
    raise