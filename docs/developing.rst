Development
===========

Instructions on how build and deploy picozero.

Build
-----

1. Update version numbers in the ``setup.py``, ``picozero/__init__.py``and ``docs/conf.py`` files.

2. Add release to ``docs/changelog.rst``

3. Run `setup.py` and create a source distribution ::

    python3 setup.py sdist

4. Upload to PyPI ::

    twine upload dist/*

5. Push all changes to ``master`` branch

6. Create a `release <https://github.com/RaspberryPiFoundation/picozero/releases>`_ in github and upload ``picozero-#-#-#.tar.gz`` source file to the release.

Documentation
-------------

The documentation site is built using Sphinx. 

Install sphinx using ::

    pip3 install sphinx

To build the documentation, run the following command from the docs directory ::

    $ make html

The website will be built in the directory docs/_build/html.

Documentation can be viewed at `picozero.readthedocs.io`_.

.. _picozero.readthedocs.io: https://picozero.readthedocs.io