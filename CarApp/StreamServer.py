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

    def stream(self, analysed_frame_queue):
        """
        stream the current analysed frame if a connection has been established
        """
        current_thread = threading.currentThread()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_address)
        # We want only one client
        self.__socket.listen(1)
        while getattr(current_thread, 'is_running', True):
            print >>sys.stderr, '[Stream Server] waiting for a connection', self.__server_address
            self.__connection, client_address = self.__socket.accept()
            try:
                print >>sys.stderr, 'connection from', client_address
                while getattr(current_thread, 'is_connected', True):
                    frame = analysed_frame_queue.get(True, None)
                    self.__connection.send(str(len(frame)).ljust(4096))
                    self.__connection.send(frame)
                    analysed_frame_queue.task_done()
                current_thread.is_connected = True
            finally:
                self.__connection.close()
