"""
Recorder module
"""
import threading
import socket
import cv2
import numpy

class Recorder(object):
    """
    Recorder class - get frame from camera continously
    """
    def __init__(self):
        self.__camera = None
        self.__encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]

    def record(self, frame_queue):
        """
        record frame
        """
        hostname = socket.gethostname()
        if 'pi' in hostname:
            self.__camera = cv2.VideoCapture(0)
        elif 'udoo' in hostname:
            self.__camera = cv2.VideoCapture(1)
        else: #computer
            self.__camera = cv2.VideoCapture(0)

        ret = self.__camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        ret = self.__camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        current_thread = threading.currentThread()
        while getattr(current_thread, 'is_running', True):
            ret, frame = self.__camera.read()
            if bool(ret) is True:
                result, encrypted_image = cv2.imencode('.jpg', frame, self.__encode_parameter)
                if bool(result) is False:
                    break
                data = numpy.array(encrypted_image)
                frame_queue.put(data.tostring())
            else:
                break

        self.__camera.release()
