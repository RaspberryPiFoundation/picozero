import os
import sys

from setuptools import setup
from setuptools.command.build_py import build_py

__project__ = "picozero"
__packages__ = ["picozero"]
__desc__ = "A beginner-friendly library for using common electronics components with the Raspberry Pi Pico. "
__version__ = "0.6.1"
__author__ = "Raspberry Pi Foundation"
__author_email__ = "learning@raspberrypi.org"
__license__ = "MIT"
__url__ = "https://github.com/RaspberryPiFoundation/picozero"
__keywords__ = [
    "raspberry",
    "pi",
    "pico",
    "electronics",
]
__classifiers__ = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Programming Language :: Python :: Implementation :: MicroPython",
]
__long_description__ = """A beginner-friendly library for using common electronics components with the Raspberry Pi Pico.

```python
from picozero import LED, Button

led = LED(1)
button = Button(2)

button.when_pressed = led.on
button.when_released = led.off
```

Documentation is available at [picozero.readthedocs.io](https://picozero.readthedocs.io/en/latest/).
"""


class build_py_without_docstrings(build_py):
    """
    Builds the package without docstrings, so that importing picozero takes
    much less memory on a Raspberry Pi Pico (see tools/strip_docstrings.py).
    """

    def run(self):
        super().run()
        try:
            sys.path.insert(
                0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
            )
            from strip_docstrings import strip_docstrings
        except Exception as e:
            # never stop picozero installing
            print("warning: not removing docstrings: {}".format(e))
            return

        for path in self.get_outputs(include_bytecode=False):
            if not path.endswith(".py"):
                continue
            with open(path, encoding="utf-8", newline="") as f:
                source = f.read()
            try:
                stripped = strip_docstrings(source)
            except Exception as e:
                print("warning: not removing docstrings from {}: {}".format(path, e))
                continue
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(stripped)


setup(
    name=__project__,
    version=__version__,
    description=__desc__,
    long_description=__long_description__,
    long_description_content_type="text/markdown",
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    classifiers=__classifiers__,
    keywords=__keywords__,
    packages=__packages__,
    cmdclass={"build_py": build_py_without_docstrings},
)
