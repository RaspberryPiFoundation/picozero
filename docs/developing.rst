Development
===========

Instructions on how to test, build and deploy picozero.

Test
----

Not sure...  pytest can probably be used but would have to mock `machine`.

Build
-----

1. Strip comments and docstrings from the source code to reduce file size (somehow).

2. Run `setup.py` and create a source distribution.:

    python3 setup.py sdist

3. Upload to PyPI:

    twine upload dist/*

Documentation
-------------

The documentation site is built using Sphinx. 

Install sphinx using :

    pip3 install sphinx

To build the documentation, run the following command from the docs directory:

    $ make html

The website will be built in the directory docs/_build/html.

