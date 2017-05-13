"""
Serial Manager Module
"""
import threading
import time
import re
import serial

class SerialManager(threading.Thread):
    """
    Class implemented to write/read on Arduino's Serial
    """
    def __init__(self, serial_name, serial_ratio):
        # thread init
        threading.Thread.__init__(self)
        # constructor parameters savers
        self.__serial_name = serial_name
        self.__serial_ratio = serial_ratio

        # thread data and storages
        self.__is_running = False
        self.__serial_file = None
        self.__dict_scanner_data = {}
        self.__list_controller_commands = []

        # terminate timer
        self.__check_timer = 0

        # locks
        self.__running_lock = threading.Lock()
        self.__serial_lock = threading.Lock()
        self.__dict_lock = threading.Lock()

    def run(self):
        self.__running_lock.acquire()
        self.__is_running = True
        self.__running_lock.release()

        self.__check_timer = time.time()

        self.__serial_lock.acquire()
        self.__serial_file = serial.Serial(self.__serial_name, self.__serial_ratio)
        self.__serial_lock.release()

        while True:
            self.__reader()
            if time.time() - self.__check_timer > 1:
                self.__running_lock.acquire()
                condition = self.__is_running
                self.__running_lock.release()
                if bool(condition) is False:
                    break
            time.sleep(400/1000) #too much locking on serial

        self.__serial_lock.acquire()
        self.__serial_file.close()
        self.__serial_lock.release()

    def stop(self):
        """
        stop the SerialManager
        """
        self.__running_lock.acquire()
        self.__is_running = False
        self.__running_lock.release()

    def __reader(self):
        self.__serial_lock.acquire()
        line = self.__serial_file.readline()
        self.__serial_lock.release()
        if line:
            if 'CAR_DATA' in line:
                self.__serial_lock.acquire()
                line = self.__serial_file.readline()
                self.__serial_lock.release()
                while 'END_CAR_DATA' not in line:
                    if line:
                        self.__store_in_dictionary(line)
                    self.__serial_lock.acquire()
                    line = self.__serial_file.readline()
                    self.__serial_lock.release()

    def __store_in_dictionary(self, line_to_store):
        """
        Convert from string to dictionary fields
        """
        line_to_store_tokenized = re.findall(r"[\w.]+", line_to_store)
        if len(line_to_store_tokenized) > 1:
            self.__dict_lock.acquire()
            self.__dict_scanner_data[line_to_store_tokenized[0]] = line_to_store_tokenized[1]
            self.__dict_lock.release()

    def __writer(self):
        for element in enumerate(self.__list_controller_commands):
            if len(element) > 1:
                self.__serial_lock.acquire()
                self.__serial_file.write(str(element[1]))
                self.__serial_lock.release()
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
        get the dictionary as a string with car states
        """
        self.__dict_lock.acquire()
        output_dict = self.__dict_scanner_data
        self.__dict_lock.release()
        output = ''
        for key, value in output_dict.items():
            output = output + str(key) + ',' + str(value) + ';'
        return output
