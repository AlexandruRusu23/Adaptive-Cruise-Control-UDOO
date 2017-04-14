"""
Serial Manager Module
"""
import threading
import time
import datetime
import re
import serial

class SerialManager(threading.Thread):
    """
    Class implemented to manipulate the Microcontroller's Serial
    """
    def __init__(self, serialName, serialRatio):
        threading.Thread.__init__(self)
        self._running_lock = threading.Lock()
        self._scanner_dict_lock = threading.Lock()
        self.__serial_file = serial.Serial(serialName, serialRatio)
        self.__list_animator_commands = []
        self.__dict_scanner_data = {}
        self._is_running = False

    def run(self):
        self._running_lock.acquire()
        self._is_running = True
        self._running_lock.release()
        while True:
            self.__reader()

            self._running_lock.acquire()
            if bool(self._is_running) is False:
                self._running_lock.release()
                break
            self._running_lock.release()
            #print self.__dict_scanner_data
        self.__serial_file.close()

    def __reader(self):
        """
        Method created to read from Microcontroller's Serial
        """
        line = self.__serial_file.readline()
        if line:
            if 'scanner_data' in line:
                line = self.__serial_file.readline()
                while 'end_scanner_data' not in line:
                    if line:
                        self.__store_in_dictionary(line)
                    line = self.__serial_file.readline()
            timest = time.time()
            timestamp = datetime.datetime.fromtimestamp(timest).strftime('%Y-%m-%d %H:%M:%S')
            self._scanner_dict_lock.acquire()
            self.__dict_scanner_data['time_collected'] = timestamp
            self._scanner_dict_lock.release()

    def __store_in_dictionary(self, line_to_store):
        """
        Convert from string to dictionary fields
        """
        line_to_store_tokenized = re.findall(r"[\w.]+", line_to_store)
        if len(line_to_store_tokenized) > 1:
            self.__dict_scanner_data[line_to_store_tokenized[0]] = line_to_store_tokenized[1]

    def __writer(self):
        """
        Method created to write on Microcontroller's Serial
        """
        for element in enumerate(self.__list_animator_commands):
            if len(element) > 1:
                self.__serial_file.write(str(element[1]))
                time.sleep(100.0 / 1000.0)
        self.__list_animator_commands = []

    def stop(self):
        """
        stop the Serial Manager
        """
        self._running_lock.acquire()
        self._is_running = False
        self._running_lock.release()

    def get_scanner_data(self):
        """
        Get the data from Serial from a dictionary which is returned by the function
        """
        self._scanner_dict_lock.acquire()
        output = self.__dict_scanner_data
        self.__dict_scanner_data = {}
        self._scanner_dict_lock.release()
        return output

    def set_scanner_commands(self, list_scanner_commands):
        """
        send a list of commands for SerialManager to be send to Microcontroller
        """
        self.__list_animator_commands = list_scanner_commands

    def execute_commands(self):
        """
        Send to Microcontroller's Serial the commands stored in __list_scanner_commands
        """
        self.__writer()
