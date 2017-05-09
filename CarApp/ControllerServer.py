"""
Controller module
In this module is provided a class that will comunicate with the
remote application in order to configure the Car states.
"""
import os
import threading
import socket
import SerialManager

PATH_ARDUINO_BOARDS = '/dev/'
SUBSTR_RASPBERRY_FILE = 'ttyACM'
SUBSTR_UDOO_FILE = 'ttyMCC'

class ControllerServer(threading.Thread):
    """
    Controller class
    Is has to comunicate with the remote app to send the setup commands
    to Car using SerialManager
    """
    def __init__(self, hostname='192.168.0.106', port=32656):
        threading.Thread.__init__(self)
        self.__serial_manager = None
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__server_address = (hostname, port)
        self.__socket = None
        self.__board_name = []

    def run(self):
        self.__is_running = True
        self.__find_board()
        if len(self.__board_name) > 0:
            hostname = socket.gethostname()
            if 'pi' in hostname:
                self.__serial_manager = SerialManager.SerialManager(self.__board_name[0], 9600)
            elif 'udoo' in hostname:
                self.__serial_manager = SerialManager.SerialManager(self.__board_name[0], 115200)
        else:
            print 'Controller Stoped'
            self.stop()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_address)
        # We want only one client
        self.__socket.listen(1)
        # Listen to infinite connection if Client disconnect
        while True:
            connection, client_address = self.__socket.accept()
            print client_address
            try:
                while True:
                    self.__is_running_lock.acquire()
                    condition = self.__is_running
                    self.__is_running_lock.release()

                    if bool(condition) is False:
                        break

                    data = connection.recv(1024) #valid
                    if data:
                        commands = []
                        commands.append(data)
                        self.__serial_manager.set_controller_commands(commands)
                        self.__serial_manager.execute_commands()
                    else:
                        break

            finally:
                # Clean up the connection
                connection.close()

            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()

            if bool(condition) is False:
                break

    def stop(self):
        """
        Stop the Controller Server
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

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
