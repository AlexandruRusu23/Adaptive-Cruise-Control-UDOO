"""
data provider client
"""
import threading
import socket

class DataProviderClient(object):
    """
    Streamer Client Class
    """
    def __init__(self, hostname, port=18089):
        self.__socket = None
        self.__server_address = (hostname, port)

    def receive_car_data(self, car_data_queue):
        """
        Receive the data about the car
        """
        current_thread = threading.currentThread()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect(self.__server_address)
        while getattr(current_thread, 'is_running', True):
            length = self.__recvall(self.__socket, 1024)
            if length is not None:
                string_data = self.__recvall(self.__socket, int(length))
                if string_data is not None:
                    car_data_queue.put(string_data, True, None)
        self.__socket.close()

    def __recvall(self, sock, count):
        """
        receive blocks of count size
        """
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

