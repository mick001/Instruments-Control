# -*- coding: utf-8 -*-

"""
Created on Thu May 9 11:51:44 2017

@author: Michy
@description:
    A short script that provides basic utility function to communicate with electronic
    instruments. This script works for both serial and GPIB communication. With some work
    around it can work also with prologix 6.0 USB-GPIB adapter.

    This file contains 2 classes:

    1. instrument class. This is the generic reference class for a generic instrument.
       instruments' specific classes inherit from this class. This class contains basic
       methods for:
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

    Before using any part of this code or any command, it is strongly recommended to
    read the instrument's reference manual and understand what operation each function
    is performing, otherwise the instrument may suffer damages.

    For more information on the Yokogawa 7651 DC source, please visit:

    http://tmi.yokogawa.com/discontinued-products/generators-sources/programmable-dc-sources/7651-programmable-dc-source/
    
    As far as I know, the Yokogawa 7651 DC source should work without additional driver
    installation, however, instruments such as Keithley's may need some additional drivers,
    please check your specific instrument's reference manual in the remote control section.
    
 
@example:
    Example at the bottom of the file
"""

#-------------------------------------------------------------------------------
# Imports

import visa # Install pyvisa: pip install pyvisa
import time

#-------------------------------------------------------------------------------
# Instrument class

class instrument(object):
    
    ##################################
    # Generic instrument class
    ##################################
    
    def __init__(self, name, port):
        
        # Initialization function:        
        # Args
        # name: name of the instrument
        # port: connection port. Can be either GPIB or serial.

        self.name = name
        self.port = port
        self.rm = visa.ResourceManager()
        print("Opening VISA session...")
        self.instr = self.rm.open_resource(port)
        print("VISA session successfully opened!")
        
    def __repr__(self):
        
        # Representation of object

        return """Instrument %s \navailable at port: %s \nwaiting for commands...""" %(self.port, self.name)
        
    def close_instrument(self):
        
        # Close VISA session (Close instrument connection)
        
        self.rm.close()
        print("Communication with instrument %s at port %s will be closed..." %(self.name, self.port))
        print("VISA session closed!")

#-------------------------------------------------------------------------------
class yokogawa7651(instrument):
    
    # Yokogawa 7651 programmable DC source object. Inherits from instrument.
    
    # Define voltage and current ranges
    voltage_ranges = {10:"R2", 100:"R3", 1000:"R4", 10000:"R5", 30000:"R6" }
    current_ranges = {1:"R4", 10:"R5", 100:"R6"}

    def print_voltage_range(self):
        
        # Print out available voltage range

        vr = [key for key in self.voltage_ranges.keys()]
        vr.sort()
        for i in vr:
            print(i, "mV")
    
    def print_current_range(self):
        
        # Print out available current range

        cr = [key for key in self.current_ranges.keys()]
        cr.sort()
        for i in cr:
            print(i, "mA")
    
    def initialize_instrument(self):

        # Initializes the entire setting data of the 7651
        
        self.instr.write("RC")
    
    def set_voltage_function(self, v_range, i_limit = None):

        # Set output in voltage mode, set the voltage range and current limit.
        # Args:
        # v_range: voltage range as specified by the instrument's manual [mV]
        # i_limit: maximum erogated current as specificed by the instrument's manual [mA]
        
        try:
            cmd_string = "F1" + self.voltage_ranges[v_range] + "E"
            self.instr.write(cmd_string)
            if i_limit:
                self.set_current_limit(i_limit)
        except Exception as e:
            print(str(e))
    
    def set_current_function(self, i_range, v_limit = None):
        
        # Set output in current mode, set the current range and voltage limit.
        # Args:
        # i_range: current range as specified by the instrument's manual [mA]
        # v_limit: maximum voltage as specificed by the instrument's manual [mV]

        try:
            cmd_string = "F5" + self.current_ranges[i_range] + "E"
            self.instr.write(cmd_string)
            if v_limit:
                self.set_voltage_limit(v_limit)
        except Exception as e:
            print(str(e))
    
    def set_voltage_limit(self, vmax):

        # Sets the voltage limit        
        # Args
        # vmax: maximum voltage [V]
        
        if vmax > 30 or vmax < 0:
            raise ValueError("Error: vmax should be in the 1 to 30 V range!")
        
        cmd_string = "LV" + str(vmax)
        self.instr.write(cmd_string)
        
    def set_current_limit(self, imax):
        
        # Sets the current limit        
        # Args
        # imax: maximum current [mA]
        
        if imax > 120 or imax < 5:
            raise ValueError("Error: imax should be in the 5 to 120 mA range!")
        
        cmd_string = "LA" + str(imax)
        self.instr.write(cmd_string)
        

    def set_output_val(self, value, polarity = "+"):
    
        # Sets the value of the voltage or current that is output in a fixed range.
        # Args:
        # value: voltage [V] or current [A] to set as output
        # polarity: either "+" (default) or "-"
    
        cmd_string = "S" + polarity + str(value) + "E"
        self.instr.write(cmd_string)
        
    def set_output_state(self, on=False):
        
        # Sets on/off the condition of the output
        # Args
        # on: set to True for the output condition to be set on "on".

        cmd_string = "O"+ str(int(on)) + "E"
        self.instr.write(cmd_string)
        
    def dc_voltage_sweep(self, v_min, v_max, step, delay, v_range, i_limit, polarity = "+"):

        # Do a quick voltage DC sweep
        # Args:
        # v_min: minimum sweep voltage [V]
        # v_max: maximum sweep voltage [V]
        # step: step of the sweep
        # delay: delay between states [s]
        # v_range: voltage range as specified by the instrument's manual [mV]
        # i_limit: maximum erogated current as specificed by the instrument's manual [mA]

        if v_min > v_max:
            raise ValueError("Error: v_min should be lower than v_max")
        
        self.set_voltage_function(v_range, i_limit)
        
        while v_min <= v_max:
            self.set_output_val(v_min, polarity)
            v_min += step
            time.sleep(delay)

#-------------------------------------------------------------------------------

# Example:
# Set the output in voltage mode within the 10V range.
# Set the output to a value of 3V with a 20mA current limit.
# Turn on the output
# Wait 10s
# Turn off the output
# Close the VISA session

if __name__ == "main":
    dc_source = yokogawa7651(name = "Yokogawa 7651", addr = "GBIP::14::INSTR")
    dc_source.set_voltage_function(v_range = 10000, i_limit = 20)
    dc_source.set_output_val(value = 3)
    dc_source.set_output_state(on = True)
    time.sleep(10)
    dc_source.set_output_state(on = False)
    dc_source.close_instrument()
    
