.. picozero: a library for controlling Raspberry Pi Pico GPIO pins with MicroPython
..
.. SPDX short identifier: MIT

Requirements
===============

A Windows, macOS or Linux computer with the `Thonny Python IDE`_ installed.

.. _Thonny Python IDE: https://thonny.org/

You can find information on how to install Thonny on the `Introduction to Raspberry Pi Pico guide`_.

.. _Introduction to Raspberry Pi Pico guide: https://learning-admin.raspberrypi.org/en/projects/introduction-to-the-pico/2

Once Thonny is installed you will need to ensure that you are using the latest MicroPython firmware. Details on how to install or update the Raspberry Pi Pico MicroPython firmware can be found on the `guide`_.

.. _guide: https://learning-admin.raspberrypi.org/en/projects/introduction-to-the-pico/3

Install picozero from PyPi in Thonny
===============

To install picozero within Thonny select **Tools** > **Manage packages...**

.. image:: images/thonny-manage-packages.jpg

Search for `picozero` on PyPi.

.. image:: images/thonny-packages-picozero.jpg

Click on install to download the package.

.. image:: images/thonny-install-package.jpg

Other install options
===============

You can use the Thonny file manager to transfer a ``picozero.py`` file to Raspberry Pi Pico.

From the **View** menu, choose to see files.

.. image:: images/thonny-view-files.jpg

Either clone the picozero `GitHub repository`_ or copy the code from the `picozero.py`_ file and save it on your main computer.

.. _GitHub repository: https://github.com/RaspberryPiFoundation/picozero
.. _picozero.py: https://raw.githubusercontent.com/RaspberryPiFoundation/picozero/master/picozero/picozero.py?token=GHSAT0AAAAAABRLTKWZDBSYBE54NJ7AIZ6MYSENI2A

In Thonny, navigate to the cloned directory or location you save the file to find the ``picozero.py`` file.

.. image:: images/thonny-navigate-downloads.jpg

Right click on the file and select the **Upload to /** option and you should see a copy of the ``picozero.py`` file on Raspberry Pi Pico.

.. image:: images/thonny-upload-files.jpg
.. image:: images/thonny-copy-picozero.jpg




Use the MicroPython interpreter
===============

Write a program to control the onboard LED
===============

Run a program on your computer
===============

Run a program on Raspberry Pi Pico
===============
