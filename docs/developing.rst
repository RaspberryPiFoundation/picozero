Development
===========

Instructions on how build and deploy picozero.

Build
-----

1. Update version numbers in the ``setup.py``, ``picozero/__init__.py``and ``docs/conf.py`` files.

2. Add release to ``docs/changelog.rst``

3. Run `setup.py` and create a source distribution.:

    python3 setup.py sdist

4. Upload to PyPI:

    twine upload dist/*

5. Push all change to ``master`` branch

6. Create a release in github and upload ``picozero-#-#-#.tar.gz`` to the release.

Documentation
-------------

The documentation site is built using Sphinx. 

Install sphinx using :

    pip3 install sphinx

To build the documentation, run the following command from the docs directory:

    $ make html

The website will be built in the directory docs/_build/html.

Documentation can be viewed at http://picozero.readthedocs.io/