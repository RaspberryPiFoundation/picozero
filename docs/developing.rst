Development
===========

Instructions on how build and deploy picozero.

Pre-requisites
--------------

To build and deploy picozero, you need to install the dependencies ::

    pip3 install twine sphinx 

Build
-----

1. Update version numbers in the ``setup.py``, ``picozero/__init__.py``, and ``docs/conf.py`` files

2. Add release to ``docs/changelog.rst``

3. Run `setup.py` and create a source distribution ::

    python3 setup.py sdist

4. Upload to PyPI ::

    twine upload dist/*

5. Push all changes to ``master`` branch

6. Create a `release <https://github.com/RaspberryPiFoundation/picozero/releases>`_ in github and upload ``picozero-#-#-#.tar.gz`` source file to the release

Documentation
-------------

The documentation site is built using Sphinx. 

Install sphinx using ::

    pip3 install sphinx

To test the documentation build, run the following command from the docs directory ::

    $ make html

The website will be built in the directory docs/_build/html.

Documentation can be viewed at `picozero.readthedocs.io`_ and is automatically built and deployed on commit.

.. _picozero.readthedocs.io: https://picozero.readthedocs.io

Tests
-----

The tests are design to be run on a Raspberry Pi Pico.

1. Install the `picozero <https://pypi.org/project/picozero/>`_ package

2. Install the `micropython-unittest <https://pypi.org/project/micropython-unittest/>`_ package

3. Copy the ``test_picozero.py`` file to the Pico

4. Run the ``test_picozero.py`` file

If a test fails, it is helpful to be able to see verbose error messages. To see error messages, you need to modify the ``lib/unittest.py`` file on the Pico.

Locate the following code in the ``run_class`` function::

    # Uncomment to investigate failure in detail
    #raise

Uncomment ``raise``::

    # Uncomment to investigate failure in detail
    raise
