"""
Main application that will run on the car
"""
import threading
import ControllerServer
import StreamerServer

class CarMain(threading.Thread):
    """
    Main Car application Class
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__controller_server = None
        self.__streamer_server = None

        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__controller_server = ControllerServer.ControllerServer()
        self.__streamer_server = StreamerServer.StreamerServer()
        self.__controller_server.start()
        self.__streamer_server.start()
        while True:
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                break

    def stop(self):
        """
        stop the entire app
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()
        self.__controller_server.stop()
        self.__streamer_server.stop()
