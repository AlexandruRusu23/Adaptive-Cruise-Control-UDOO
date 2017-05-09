"""
Streamer module
This module has to provide the live from the camera to the
remote application
"""
import threading
import time
import socket
import sys
import cv2
import numpy

class StreamerServer(threading.Thread):
    """
    Streamer class
    """
    def __init__(self, host='192.168.0.106', port=8089):
        threading.Thread.__init__(self)
        self.__socket = None
        self.__server_adress = (host, port)
        self.__camera = None
        self.__connection = None
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        self.__check_timer = None

    def run(self):
        self.__check_timer = time.time()
        self.__is_running = True
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_adress)
        # We want only one client
        self.__socket.listen(1)
        while True:
            print >>sys.stderr, 'waiting for a connection'
            print self.__server_adress
            self.__connection, client_address = self.__socket.accept()
            try:
                print >>sys.stderr, 'connection from', client_address

                hostname = socket.gethostname()
                if 'pi' in hostname:
                    self.__camera = cv2.VideoCapture(0)
                elif 'udoo' in hostname:
                    self.__camera = cv2.VideoCapture(1)
                else: #computer
                    self.__camera = cv2.VideoCapture(0)

                ret = self.__camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                ret = self.__camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

                while True:
                    ret, current_frame = self.__camera.read()
                    if bool(ret) is True:
                        result, encrypted_image =                \
                            cv2.imencode('.jpg', current_frame, self.__encode_parameter)
                        if bool(result) is False:
                            break
                        data = numpy.array(encrypted_image)
                        string_data = data.tostring()

                        self.__connection.send(str(len(string_data)).ljust(4096))
                        self.__connection.send(string_data)
                    else:
                        break
                    if time.time() - self.__check_timer > 1:
                        self.__is_running_lock.acquire()
                        condition = self.__is_running
                        self.__is_running_lock.release()
                        if bool(condition) is False:
                            break
                        self.__check_timer = time.time()

            finally:
                self.__connection.close()
                self.__camera.release()
                self.stop()

            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                self.__connection.close()
                self.__camera.release()
                break

    def stop(self):
        """
        Stop the Streamer Server
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()
