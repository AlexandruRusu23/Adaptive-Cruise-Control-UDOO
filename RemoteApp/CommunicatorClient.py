"""
ComunicatorClient module
"""
import threading
import socket
import time

class CommunicatorClient(object):
    """
    Controller Client Class
    """
    def __init__(self, hostname, port=32656):
        self.__socket = None
        self.__server_address = (hostname, port)

    def send_commands(self, commands_queue):
        """
        Send Commands to car to be executed
        """
        current_thread = threading.currentThread()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect(self.__server_address)
        while getattr(current_thread, 'is_running', True):
            command = commands_queue.get(True, None)
            self.__socket.sendall(str(command))
            time.sleep(100.0 / 1000.0)
        self.__socket.close()
