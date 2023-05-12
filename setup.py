from setuptools import setup

__project__ = 'picozero'
__packages__ = ['picozero']
__desc__ = 'A beginner-friendly library for using common electronics components with the Raspberry Pi Pico. '
__version__ = '0.4.2
__author__ = "Raspberry Pi Foundation"
__author_email__ = 'learning@raspberrypi.org'
__license__ = 'MIT'
__url__ = 'https://github.com/RaspberryPiFoundation/picozero'
__keywords__ = [
    'raspberry',
    'pi',
    'pico',
    'electronics',
]
__classifiers__ = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Programming Language :: Python :: Implementation :: MicroPython',
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

setup(
    name=__project__,
    version=__version__,
    description=__desc__,
    long_description=__long_description__,
    long_description_content_type='text/markdown',
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    classifiers=__classifiers__,
    keywords=__keywords__,
    packages=__packages__,
)