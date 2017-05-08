"""
Recorder module
"""
import threading
import cv2
import numpy

class Recorder(threading.Thread):
    """
    Recorder class - get frame from camera continously
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__camera = None
        self.__frame = None
        self.__frame_lock = threading.Lock()
        self.__frame_encrypted = None
        self.__frame_encrypted_lock = threading.Lock()
        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__camera = cv2.VideoCapture(0) #get rid of the 0 hardcodation
        while True:
            self.__frame_lock.acquire()
            ret, self.__frame = self.__camera.read()
            self.__frame_lock.release()
            if bool(ret) is True:
                encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                self.__frame_lock.acquire()
                result, encryp_image = cv2.imencode('.jpg', self.__frame, encode_parameter)
                self.__frame_lock.release()
                if bool(result) is False:
                    break
                data = numpy.array(encryp_image)
                self.__frame_encrypted_lock.acquire()
                self.__frame_encrypted = data.tostring()
                self.__frame_encrypted_lock.release()
            else:
                break
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                break
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
