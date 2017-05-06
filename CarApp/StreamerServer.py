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

class StreamerServer(threading.Thread):
    """
    Streamer class
    """
    def __init__(self, host='192.168.0.101', port=8089):
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
            print >>sys.stderr, 'waiting for a connection'
            print self.__server_adress
            connection, client_address = self.__socket.accept()
            try:
                print >>sys.stderr, 'connection from', client_address
                camera = cv2.VideoCapture(0)

                while True:
                    ret, current_frame = camera.read()
                    if bool(ret) is True:
                        encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                        result, encryp_image = cv2.imencode('.jpg', current_frame, encode_parameter)
                        if bool(result) is False:
                            break
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
                connection.close()
                camera.release()
                break

    def stop(self):
        """
        Stop the Streamer Server
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()
