"""
Serial Manager Module
"""
import time
import serial

class SerialManager(object):
    """
    Class implemented to manipulate the Microcontroller's Serial
    """
    def __init__(self, serialName, serialRatio):
        self.__serial_file = serial.Serial(serialName, serialRatio)
        self.__list_controller_commands = []

    def __writer(self):
        """
        Method created to write on Microcontroller's Serial
        """
        for element in enumerate(self.__list_controller_commands):
            if len(element) > 1:
                self.__serial_file.write(str(element[1]))
                time.sleep(100.0 / 1000.0)
        self.__list_controller_commands = []

    def set_controller_commands(self, list_controller_commands):
        """
        send a list of commands for SerialManager to be send to Microcontroller
        """
        self.__list_controller_commands = list_controller_commands

    def execute_commands(self):
        """
        Send to Microcontroller's Serial the commands stored in __list_controller_commands
        """
        self.__writer()
