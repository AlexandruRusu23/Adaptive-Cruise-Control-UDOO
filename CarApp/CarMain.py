"""
Main application that will run on the car
"""
import socket
import threading
import ControllerServer
import StreamerServer
import Recorder

class CarMain(threading.Thread):
    """
    Main Car application Class
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__recorder = None
        self.__controller_server = None
        self.__streamer_server = None

        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__recorder = Recorder.Recorder()
        self.__controller_server = ControllerServer.ControllerServer(self.get_ip_address())
        self.__streamer_server = StreamerServer.StreamerServer(self.get_ip_address())
        self.__recorder.start()
        self.__controller_server.start()
        self.__streamer_server.start()
        while True:
            try:
                if bool(self.__streamer_server.is_connected()) is True:
                    self.__streamer_server.set_encrypted_frame(             \
                        self.__recorder.get_encrypted_frame())

                self.__is_running_lock.acquire()
                condition = self.__is_running
                self.__is_running_lock.release()
                if bool(condition) is False:
                    break
            except KeyboardInterrupt:
                self.stop()

        self.__controller_server.join()
        self.__streamer_server.join()
        self.__recorder.join()

    def stop(self):
        """
        stop the entire app
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()
        self.__controller_server.stop()
        self.__streamer_server.stop()
        self.__recorder.stop()

    def get_ip_address(self):
        """
        get your current ip address
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]

    def get_frame(self):
        """
        get clean frame from Recorder
        """
        return self.__recorder.get_frame()

    def get_encrypted_frame(self):
        """
        get encrypted frame from Recorder
        """
        return self.__recorder.get_encrypted_frame()


if __name__ == '__main__':
    CAR_MAIN = CarMain()
    CAR_MAIN.start()
