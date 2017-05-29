"""
Controller module
"""
import threading
import socket
import time

class ControllerClient(threading.Thread):
    """
    Controller Client Class
    """
    def __init__(self, hostname='192.168.0.103', port=32656):
        threading.Thread.__init__(self)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_address = (hostname, port)
        self.__command_list = []
        self.__command_list_lock = threading.Lock()
        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__socket.connect(self.__server_address)
        commands = []
        while True:
            self.__command_list_lock.acquire()
            if self.__command_list:
                commands = self.__command_list
                self.__command_list = []
            self.__command_list_lock.release()

            if commands:
                for element in enumerate(commands):
                    if len(element) > 1:
                        self.__socket.sendall(str(element[1]))
                        time.sleep(50.0 / 1000.0)
                commands = []
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                break
        self.__socket.close()

    def stop(self):
        """
        Stop the Controller Client
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

    def execute_command(self, command_type):
        """
        give a command and it will be sent to CarApp
        """
        if command_type == 'GO_LEFT':
            self.__command_list.append('4/')
        elif command_type == 'GO_RIGHT':
            self.__command_list.append('5/')
        elif command_type == 'SPEED_UP':
            self.__command_list.append('1/2/')
        elif command_type == 'SPEED_DOWN':
            self.__command_list.append('2/')
        elif command_type == 'BRAKE':
            self.__command_list.append('3/')
        elif command_type == 'REAR':
            self.__command_list.append('6/')
        else:
            self.__command_list.append(str(command_type))
