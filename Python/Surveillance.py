"""
Surveillance Module
"""
import threading
import time
import datetime
import cv2

class Surveillance(threading.Thread):
    """
    Surveillance class
    """
    #static field to increment the id of the camera to prevent the cases with more than one camera
    idCamera = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self._running_lock = threading.Lock()
        self._is_running = False
        self._camera = None

    def run(self):
        self._is_running = True
        self._camera = cv2.VideoCapture(Surveillance.idCamera)
        Surveillance.idCamera = Surveillance.idCamera + 1
        self.__record()
        cv2.destroyAllWindows()

    def __record(self):
        while True:
            ret, frame = self._camera.read()
            cv2.imshow('Frame', frame)

            self._running_lock.acquire()
            if bool(self._is_running) is False:
                self._running_lock.release()
                break
            self._running_lock.release()

    def stop(self):
        """
        Stop the entire running thread
        """
        self._running_lock.acquire()
        self._is_running = False
        self._running_lock.release()
