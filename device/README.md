# picozero for the Raspberry Pi Pico

These files are copies of the ones in [`picozero/`](../picozero) without their
docstrings, for installing on a Raspberry Pi Pico with mip or by hand.

MicroPython holds every docstring in memory while it compiles `picozero.py`,
which takes most of the free memory on a Pico with an RP2040, and it throws
them away afterwards. The docstrings are only needed for the documentation, so
they're left out here. Line numbers are the same as in `picozero/`, so error
messages from a Pico match the source.

**Don't edit these files.** Change the files in `picozero/`, then update these
with:

    python3 tools/strip_docstrings.py

The package on PyPI (which Thonny installs) is built without docstrings by
`setup.py`, so it doesn't use these files.
