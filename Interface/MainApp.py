"""
Main App doc
"""
import threading
import Controller

class MainApp(threading.Thread):
    """
    Main App Doc
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__controller = Controller.Controller()
        