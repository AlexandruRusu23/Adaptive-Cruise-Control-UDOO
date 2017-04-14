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

    def __init__(self, frame_width, frame_height, fps_camera):
        threading.Thread.__init__(self)
        self._running_lock = threading.Lock()
        self._is_running = False
        self._camera = cv2.VideoCapture(Surveillance.idCamera)
        Surveillance.idCamera = Surveillance.idCamera + 1
        self._fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._fps_camera = fps_camera
        file_name = self.__get_file_name()
        frame_size = (self._frame_width, self._frame_height)
        self._file_out = cv2.VideoWriter(file_name, self._fourcc, self._fps_camera, frame_size)
        self._current_time = time.time()

    def run(self):
        self._is_running = True
        self._current_time = time.time()
        self.__record()
        self._camera.release()
        self._file_out.release()
        cv2.destroyAllWindows()

    def __record(self):
        while self._camera.isOpened():
            ret, frame = self._camera.read()
            if bool(ret) is True:
                if (time.time() - self._current_time) > 10:
                    self._file_out.release()
                    file_name = self.__get_file_name()
                    frame_size = (self._frame_width, self._frame_height)
                    self._file_out = \
                        cv2.VideoWriter(file_name, self._fourcc, self._fps_camera, frame_size)
                    self._current_time = time.time()

                self._file_out.write(frame)

                self._running_lock.acquire()
                if bool(self._is_running) is False:
                    self._running_lock.release()
                    break
                self._running_lock.release()

            else:
                self.stop()
                break

    def stop(self):
        """
        Stop the entire running thread
        """
        self._running_lock.acquire()
        self._is_running = False
        self._running_lock.release()

    def __get_file_name(self):
        return 'VIDEO' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi'
