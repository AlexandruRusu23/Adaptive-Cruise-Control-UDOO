"""
ComunicatorClient module
"""
import Queue
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

        __thread_timer = time.time()

        while getattr(current_thread, 'is_running', True):
            if time.time() - __thread_timer > 100.0 / 1000.0:
                __thread_timer = time.time()
                try:
                    command = commands_queue.get(False)
                except Queue.Empty:
                    continue
                self.__socket.sendall(str(command))
        self.__socket.close()
