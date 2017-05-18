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
    def __init__(self, hostname='192.168.0.104', port=8089):
        threading.Thread.__init__(self)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_address = (hostname, port)
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__frame = None
        self.__frame_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__socket.connect(self.__server_address)
        while True:
            length = self.recvall(self.__socket, 4096)
            if length is None:
                break
            string_data = self.recvall(self.__socket, int(length))
            if string_data is None:
                break
            data = numpy.fromstring(string_data, dtype='uint8')

            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                break

            self.__frame_lock.acquire()
            self.__frame = cv2.imdecode(data, 1)
            self.__frame_lock.release()

        self.__socket.close()

    def stop(self):
        """
        stop the streamer client
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

    def get_frame(self):
        """
        get the current frame
        """
        self.__frame_lock.acquire()
        output = self.__frame
        self.__frame_lock.release()
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
