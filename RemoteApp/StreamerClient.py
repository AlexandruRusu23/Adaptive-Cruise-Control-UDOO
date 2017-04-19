"""
Streamer Module
"""
import threading
import socket
import cv2
import numpy

class StreamerClient(threading.Thread):
    """
    Streamer Client Class
    """
    def __init__(self, hostname='192.168.0.107', port=8089):
        threading.Thread.__init__(self)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_adress = (hostname, port)
        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__socket.connect(self.server_address)
        while True:
            length = self.recvall(self.__socket, 4096)
            if length is None:
                break
            string_data = self.recvall(self.__socket, int(length))
            if string_data is None:
                break
            data = numpy.fromstring(string_data, dtype='uint8')

            frame = cv2.imdecode(data, 1)
            cv2.imshow('frameClient', frame)
            k = cv2.waitKey(33)
            if k == 27:
                break

        self.__socket.close()

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
