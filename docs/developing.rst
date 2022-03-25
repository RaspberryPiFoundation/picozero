Development
===========

Instructions on how build and deploy picozero.

Build
-----

1. Run `setup.py` and create a source distribution.:

    python3 setup.py sdist

2. Upload to PyPI:

    twine upload dist/*

Documentation
-------------

The documentation site is built using Sphinx. 

Install sphinx using :

    pip3 install sphinx

To build the documentation, run the following command from the docs directory:

    $ make html

The website will be built in the directory docs/_build/html.

Documentation can be viewed at http://picozero.readthedocs.io/