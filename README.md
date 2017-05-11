## VISA instrument control in Python

A short script that provides basic utility function to communicate with electronic
instruments. This script works for both serial and GPIB communication. With some work
around it can work also with prologix 6.0 USB-GPIB adapter.

This repository contains 2 classes:

1. instrument class. This is the generic reference class for a generic instrument. Instruments' specific classes inherit from this class. This class contains basic methods for:
- VISA session initialization
- Object representation
- Terminating VISA session.

2. A specific example of application with the Yokogawa 7651 DC source.
This class implements the most common tasks for remote control of a 7651 DC source.
The following basic commands have been implemented:
- Initialize instrument
- Set DC voltage function (1)
- Set DC current function (2)
- Set current limit (within (1))
- Set voltage limit (within (2))
- Set output value
- Set output state
- Do a DC voltage sweep

Before using any part of this code or any command, it is strongly recommended to read the instrument's reference manual and understand what operation each function is performing, otherwise the instrument may suffer damages.

For more information on the Yokogawa 7651 DC source, please visit:

http://tmi.yokogawa.com/discontinued-products/generators-sources/programmable-dc-sources/7651-programmable-dc-source/
    
As far as I know, the Yokogawa 7651 DC source should work without additional driver installation, however, instruments such as Keithley's may need some additional drivers, please check your specific instrument's reference manual in the remote control section.

## Example:
An example is provided at the bottom of the file visa_interface.py
