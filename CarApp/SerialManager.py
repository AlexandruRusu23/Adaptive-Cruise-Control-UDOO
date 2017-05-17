"""
Serial Manager Module
"""
import time
import serial

class SerialManager(object):
    """
    Class implemented to write/read on Arduino's Serial
    """
    def __init__(self, serial_name, serial_ratio):
        # constructor parameters savers
        self.__serial_name = serial_name
        self.__serial_ratio = serial_ratio

        # thread data and storages
        self.__serial_file = None
        self.__list_controller_commands = []

    def connect(self):
        """
        connect to the arduino board
        """
        self.__serial_file = serial.Serial(self.__serial_name, self.__serial_ratio)

    def __writer(self):
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

    def get_car_data(self):
        """
        get the states about the car
        """
        return 'hello'
