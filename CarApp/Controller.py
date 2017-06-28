"""
Controller module
"""
import os
import time
import Queue
import socket
import threading
import SerialManager

PATH_ARDUINO_BOARDS = '/dev/'
SUBSTR_RASPBERRY_FILE = 'ttyACM'
SUBSTR_UDOO_FILE = 'ttyMCC'

class Controller(object):
    """
    Controller class
    Is has to comunicate with the Arduino to send commands
    to Car using SerialManager
    """
    def __init__(self):
        self.__serial_manager = None
        self.__board_name = []

        self.__serial_connected = False
        self.__serial_connected_lock = threading.Lock()

    def __find_board(self):
        """
        Find the arduino file
        """
        self.__board_name = []
        path_string = PATH_ARDUINO_BOARDS
        files_to_search_in = os.listdir(path_string)
        file_substr = [SUBSTR_RASPBERRY_FILE, SUBSTR_UDOO_FILE]
        for current_file in files_to_search_in:
            for current_substr in file_substr:
                if current_substr in current_file:
                    self.__board_name.append(path_string + current_file)

    def __connect(self):
        """
        connect via SerialManager to Arduino Board
        """
        self.__find_board()
        if len(self.__board_name) > 0:
            hostname = socket.gethostname()
            if 'pi' in hostname:
                self.__serial_manager = SerialManager.SerialManager(self.__board_name[0], 9600)
            elif 'udoo' in hostname:
                self.__serial_manager = SerialManager.SerialManager(self.__board_name[0], 115200)
            else: #computer
                self.__serial_manager = SerialManager.SerialManager(self.__board_name[0], 9600)
        else:
            return False

        self.__serial_connected = True
        return True

    def __is_connected(self):
        self.__serial_connected_lock.acquire()
        output = self.__serial_connected
        self.__serial_connected_lock.release()
        return output

    def __start_serial_manager(self):
        """
        Start the SerialManager to read car states
        """
        self.__serial_connected_lock.acquire()
        if bool(self.__connect()) is True:
            self.__serial_manager.start()
            self.__serial_connected = True
        self.__serial_connected_lock.release()

    def get_car_data(self, car_data_queue):
        """
        get the dictionary with car states from SerialManager
        """
        current_thread = threading.currentThread()

        if bool(self.__is_connected()) is False:
            self.__start_serial_manager()

        __thread_timer = time.time()

        while getattr(current_thread, 'is_running', True):
            if time.time() - __thread_timer > 100.0 / 1000.0:
                self.__serial_connected_lock.acquire()
                condition = self.__serial_connected
                self.__serial_connected_lock.release()
                if bool(condition) is False:
                    break

                car_data_dict = self.__serial_manager.get_car_data()
                if len(car_data_dict) > 0:
                    while getattr(current_thread, 'is_running', True):
                        try:
                            car_data_queue.put(car_data_dict, False)
                        except Queue.Full:
                            continue
                        break
                __thread_timer = time.time()

        self.__serial_manager.stop()
        self.__serial_manager.join()

    def send_commands(self, commands_queue):
        """
        send commands to SerialManager
        """
        current_thread = threading.currentThread()

        if bool(self.__is_connected()) is False:
            self.__start_serial_manager()

        __thread_timer = time.time()

        while getattr(current_thread, 'is_running', True):
            if time.time() - __thread_timer > 100.0 / 1000.0:
                __thread_timer = time.time()
                try:
                    commands_list = [commands_queue.get(False)]
                except Queue.Empty:
                    continue

                self.__serial_manager.set_controller_commands(commands_list)
                self.__serial_manager.execute_commands()
                commands_queue.task_done()

        self.__serial_manager.stop()
        self.__serial_manager.join()
