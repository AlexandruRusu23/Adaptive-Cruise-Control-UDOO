"""
Analyser module
"""
import threading
import numpy

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
        current_thread = threading.current_thread()
        while getattr(current_thread, 'is_running', True):
            string_data = frame_queue.get(True, None)
            #data = numpy.fromstring(string_data, dtype='uint8')
            #self.__current_frame = cv2.imdecode(data, 1)
            frame_queue.task_done()
            analysed_frame_queue.put(string_data)
            #autonomous_states_queue.put()
            #commands_queue.put()
