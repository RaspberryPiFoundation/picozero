# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

# Mock out certain modules while building documentation
class Mock:
    __all__ = []
    def __init__(self, *args, **kw): pass
    def __call__(self, *args, **kw): return Mock()
    def __mul__(self, other): return Mock()
    def __and__(self, other): return Mock()
    def __bool__(self): return False
    def __nonzero__(self): return False
    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        else:
            return Mock()

sys.modules['machine'] = Mock()
sys.modules['micropython'] = Mock()

# add the ticks_ms function to time (as it is in micropython)
import time
setattr(time, 'ticks_ms', lambda x: None)

# -- Project information -----------------------------------------------------

project = 'picozero'
copyright = '2022, Raspberry Pi Foundation'
author = 'Raspberry Pi Foundation'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc', 
    'sphinx.ext.viewcode', 
    'sphinx.ext.intersphinx'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
if on_rtd:
    html_theme = 'sphinx_rtd_theme'
    #html_theme_options = {}
    html_sidebars = {
        '**': [
            'globaltoc.html',
            'relations.html',
            'searchbox.html',
        ],
    }
else:
    html_theme = 'alabaster'
    #html_theme_options = {}
    #html_sidebars = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Autodoc configuration ------------------------------------------------

autodoc_member_order = 'groupwise'
autodoc_default_flags = ['members']