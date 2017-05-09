"""
Analyser module
"""
import threading

class Analyser(threading.Thread):
    """
    Analyser class
    - responsible to analyse the current frame
    - detect lanes, cars, obstacles, road signs, etc
    and send the commands to SerialManager
    """
    def __init__(self):
        threading.Thread.__init__(self)
