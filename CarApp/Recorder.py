"""
Recorder module
"""
import threading
import time
import socket
import cv2
import numpy

class Recorder(threading.Thread):
    """
    Recorder class - get frame from camera continously
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__camera = None
        self.__frame_encrypted = None
        self.__frame_encrypted_lock = threading.Lock()
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        self.__check_timer = None

    def run(self):
        self.__check_timer = time.time()
        self.__is_running = True
        hostname = socket.gethostname()
        if 'pi' in hostname:
            self.__camera = cv2.VideoCapture(0)
        elif 'udoo' in hostname:
            self.__camera = cv2.VideoCapture(1)
        else: #computer
            self.__camera = cv2.VideoCapture(0)

        while True:
            ret, frame = self.__camera.read()
            if bool(ret) is True:
                result, encrypted_image = cv2.imencode('.jpg', frame, self.__encode_parameter)
                if bool(result) is False:
                    break
                data = numpy.array(encrypted_image)
                self.__frame_encrypted_lock.acquire()
                self.__frame_encrypted = data.tostring()
                self.__frame_encrypted_lock.release()
            else:
                break
            if time.time() - self.__check_timer > 1:
                self.__is_running_lock.acquire()
                condition = self.__is_running
                self.__is_running_lock.release()
                if bool(condition) is False:
                    break
                self.__check_timer = time.time()

        self.__camera.release()

    def stop(self):
        """
        Stop the Recorder
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

    def get_frame(self):
        """
        get clean frame
        """
        self.__frame_lock.acquire()
        output = self.__frame
        self.__frame_lock.release()
        return output

    def get_encrypted_frame(self):
        """
        get encrypted frame (jpeg compression)
        """
        self.__frame_encrypted_lock.acquire()
        output = self.__frame_encrypted
        self.__frame_encrypted_lock.release()
        return output
