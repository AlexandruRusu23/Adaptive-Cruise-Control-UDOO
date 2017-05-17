"""
Analyser module
"""
import threading
import os
import sys
import csv
import cv2
import glob
import numpy as np
import numpy.matlib
import math
import os

class Analyser(object):
    """
    Analyser class
    - responsible to analyse the current frame
    - detect lanes, cars, obstacles, road signs, etc
    and send the commands to SerialManager
    """
    def __init__(self):
        self.__current_frame = None

    def analyse(self, frame_queue, autonomous_states_queue, commands_queue, analysed_frame_queue):
        """
        get the current frame from FRAME_QUEUE of CarManager and analyse
        """
        current_thread = threading.currentThread()
        while getattr(current_thread, 'is_running', True):
            string_data = frame_queue.get(True, None)
            frame = numpy.fromstring(string_data, dtype='uint8')
            self.__current_frame = cv2.imdecode(frame, 1)
            frame_queue.task_done()

            # analysed_frame_queue.put(, True, None)
            # analysed_frame_queue.task_done()

            result, encrypted_image = cv2.imencode('.jpg', frame, self.__encode_parameter)
            if bool(result) is False:
                break
            data = numpy.array(encrypted_image)
            analysed_frame_queue.put(data.to_string())
            #autonomous_states_queue.put()
            #commands_queue.put()
