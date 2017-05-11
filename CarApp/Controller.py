"""
Controller module
"""
import os
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
            print 'Controller Stoped'
            self.__stop_serial_manager()

        print 'Serial Manager connected to', self.__board_name[0]

    def __start_serial_manager(self):
        """
        Start the SerialManager to read car states
        """
        self.__connect()
        self.__serial_manager.start()
        print 'Serial Manager reading thread has been started'

    def __stop_serial_manager(self):
        """
        Stop the SerialManager
        """
        self.__serial_manager.stop()
        print 'Serial Manager thread has been stopped'
        self.__serial_manager.join()

    def get_car_data(self):
        """
        get the dictionary with car states from SerialManager
        """
        print self.__serial_manager.get_car_data()

    def send_commands(self, commands_queue):
        """
        send commands to SerialManager
        """
        current_thread = threading.currentThread()
        self.__start_serial_manager()
        while getattr(current_thread, 'is_running', True):
            commands_list = [commands_queue.get(True, None)]
            self.__serial_manager.set_controller_commands(commands_list)
            self.__serial_manager.execute_commands()
            commands_queue.task_done()
        self.__stop_serial_manager()
