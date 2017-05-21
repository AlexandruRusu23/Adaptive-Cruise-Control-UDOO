"""
data provider client
"""
import threading
import socket

class DataProviderClient(threading.Thread):
    """
    Streamer Client Class
    """
    def __init__(self, hostname='192.168.0.105', port=18089):
        threading.Thread.__init__(self)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_address = (hostname, port)
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__car_data = None
        self.__car_data_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__socket.connect(self.__server_address)
        while True:
            length = self.recvall(self.__socket, 1024)
            if length is None:
                break
            string_data = self.recvall(self.__socket, int(length))
            if string_data is None:
                break

            self.__car_data_lock.acquire()
            self.__car_data = string_data
            self.__car_data_lock.release()

            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                break

        self.__socket.close()

    def stop(self):
        """
        stop the data provider client
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

    def get_car_data(self):
        """
        get the current data about the car
        """
        self.__car_data_lock.acquire()
        output = self.__car_data
        self.__car_data_lock.release()
        return output

    def recvall(self, sock, count):
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

