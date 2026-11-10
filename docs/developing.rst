Development
===========

Instructions on how build and deploy picozero.

The docstrings in ``picozero/picozero.py`` are only used for this documentation. MicroPython holds every docstring in memory while it compiles ``picozero.py`` on a Raspberry Pi Pico, which takes most of the free memory on an RP2040, so the copies that are installed on a Pico don't have them: ``setup.py`` removes them when the package that pip and Thonny install is built, and ``tools/strip_docstrings.py`` writes the copy in ``device/`` that mip and the manual install use. Line numbers in these copies are the same as in the source.

Pre-requisites
--------------

To build and deploy picozero, you need to install the dependencies ::

    pip3 install twine sphinx 

Build
-----

1. Update version numbers in the ``setup.py``, ``package.json``, ``picozero/__init__.py``, and ``docs/conf.py`` files

2. Add release to ``docs/changelog.rst``

3. Update the copy of picozero without docstrings in ``device/``, which mip and the manual install use ::

    python3 tools/strip_docstrings.py

4. Run ``setup.py`` and create a source distribution ::

    python3 setup.py sdist

5. Upload to PyPI ::

    twine upload dist/*

6. Push all changes to the ``main`` branch

7. Create a `release <https://github.com/RaspberryPiFoundation/picozero/releases>`_ in github and upload ``picozero-#-#-#.tar.gz`` source file to the release

Documentation
-------------

The documentation site is built using Sphinx. 

Install sphinx using ::

    pip3 install sphinx

To test the documentation build, run the following command from the docs directory ::

    make html

The website will be built in the directory docs/_build/html.

Documentation can be viewed at `picozero.readthedocs.io`_ and is automatically built and deployed on push to github.

.. _picozero.readthedocs.io: https://picozero.readthedocs.io

Tests
-----

The tests are designed to be run on a Raspberry Pi Pico.

1. Install the `picozero <https://pypi.org/project/picozero/>`_ package

2. Install the `micropython-unittest <https://pypi.org/project/micropython-unittest/>`_ package

3. Copy the ``test_picozero.py`` file to the Pico

4. Run the ``test_picozero.py`` file

To test changes that haven't been released, run ``python3 tools/strip_docstrings.py`` and copy the ``device/picozero`` folder to the ``lib`` folder on the Pico instead of installing the package. Don't use the ``picozero`` folder: its docstrings leave too little memory on a Pico with an RP2040 to run the tests.

If a test fails, it is helpful to be able to see verbose error messages. To see error messages, you need to modify the ``lib/unittest.py`` file on the Pico.

Locate the following code in the ``run_class`` function::

    # Uncomment to investigate failure in detail
    #raise

Uncomment ``raise``::

    # Uncomment to investigate failure in detail
    raise
