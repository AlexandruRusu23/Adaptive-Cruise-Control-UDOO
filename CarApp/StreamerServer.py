"""
Streamer module
This module has to provide the live from the camera to the
remote application
"""
import threading
import socket
import sys
import cv2
import numpy

class Streamer(threading.Thread):
    """
    Streamer class
    """
    def __init__(self, host='192.168.0.104', port=8088):
        threading.Thread.__init__(self)
        self.__socket = None
        self.__server_adress = (host, port)

        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_adress)
        # We want only one client
        self.__socket.listen(1)
        while True:
            connection, client_address = self.__socket.accept()
            try:
                print >>sys.stderr, 'connection from', client_address
                camera = cv2.VideoCapture(0)

                #current_time = time.time()

                while True:
                    ret, current_frame = cap.read()
                    if bool(ret) is True:
                        encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                        result, encryp_image = cv2.imencode('.jpg', current_frame, encode_parameter)
                        data = numpy.array(encryp_image)
                        string_data = data.tostring()

                        connection.send(str(len(string_data)).ljust(4096))
                        connection.send(string_data)
                    else:
                        break
                    self.__is_running_lock.acquire()
                    condition = self.__is_running
                    self.__is_running_lock.release()
                    if bool(condition) is False:
                        break

            finally:
                connection.close()
                camera.release()
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                break
