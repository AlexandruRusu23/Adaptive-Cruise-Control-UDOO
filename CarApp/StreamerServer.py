"""
Streamer Server module
"""
import threading
import socket
import sys

class StreamerServer(object):
    """
    streamer server class
    """
    def __init__(self, host, port=8089):
        self.__socket = None
        self.__server_address = (host, port)
        self.__connection = None

    def stream(self, frame_queue):
        """
        stream the current analysed frame if a connection has been established
        """
        current_thread = threading.currentThread()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_address)
        # We want only one client
        self.__socket.listen(1)
        while getattr(current_thread, 'is_running', True):
            self.__connection, client_address = self.__socket.accept()
            try:
                current_thread.is_connected = True
                while getattr(current_thread, 'is_connected', True):
                    frame = frame_queue.get(True, None)
                    self.__connection.send(str(len(frame)).ljust(4096))
                    self.__connection.send(frame)
                    frame_queue.task_done()
            finally:
                self.__connection.close()
        self.__socket.close()
