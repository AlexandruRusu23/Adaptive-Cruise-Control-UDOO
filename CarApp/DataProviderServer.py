"""
Data Provider Server module
"""
import sys
import threading
import socket

class DataProviderServer(object):
    """
    data provider server class
    """
    def __init__(self, host, port=18089):
        self.__socket = None
        self.__server_address = (host, port)
        self.__connection = None

    def provide(self, car_data_queue):
        """
        provide the remote app with car data if a connection has been established
        """
        current_thread = threading.currentThread()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_address)
        # We want only one client
        self.__socket.listen(1)
        while getattr(current_thread, 'is_running', True):
            self.__connection, client_address = self.__socket.accept()
            try:
                while getattr(current_thread, 'is_connected', True):
                    states = car_data_queue.get(True, None)
                    self.__connection.send(str(len(states)).ljust(1024))
                    self.__connection.send(states)
                    car_data_queue.task_done()
                current_thread.is_connected = True
            finally:
                self.__connection.close()
        self.__socket.close()
