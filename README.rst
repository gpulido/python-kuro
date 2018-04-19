Python control of Pioneer Kuro TV through RS232 
======================================================

|PyPI version|

A simple Python API for controlling Pioneer Kuro TV's using an rs232 serial port.

Supported hardware:  PDP-LX5090/5090H/6090/6090H and KRP-500A/600A series

TV Configuration 
----------------
To configure the serial port in the Kuro TV the following steps must be done:

1.1 Baud rate selection
a) Entering integrator menu:
Push Menu key and Power key within 3sec. Following default Integrator menu will appear.
RS232C baud rate setting
 
b) Exit from integrator menu:
Push Home Menu key then close Integrator menu and return to normal operation.
 
c) RS232C baud rate setting
UART SELECT: 1200bps/2400bps/4800bps/9600bps/19200bps/38400bps

Example of use
--------------

Create a new instance of the gateway:

.. code-block:: python

    gat = Gateway(portname, baudrate)


portname is the name of the serial port where the serial is listed on the os. 
It can be also be defined as an rfr2217 url.
baudrate value on which the TV has been set (see TV configuration section)
Please refer to the serial library documentation.

To send a command to the tv:

.. code-block:: python

    gat.executeCmd(command, parameter)

this will send any command if it is properly configured.

On the protocol.py file several commands are already configured and can be 
send directly to the gateway. For example to mute the TV:

.. code-block:: python

    gat.executeCommand(MutedCommand(MutedState.ON))

Please review the protocol.py file for a complete list of implemented commands.

.. |PyPI version| image:: https://badge.fury.io/py/python-kuro.svg
   :target: https://badge.fury.io/py/python-kuro









