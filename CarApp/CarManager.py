"""
Car Manager module
 - responsible for every components
"""
import Queue
import threading
import socket
import Recorder
import Controller
import Analyser
import StreamServer
import UserComunicatorServer
import time

FRAME_QUEUE = Queue.Queue(1)
COMMANDS_QUEUE = Queue.Queue(1)
AUTONOMOUS_STATES_QUEUE = Queue.Queue(1)
ANALYSED_FRAME_QUEUE = Queue.Queue(1)
USER_COMMANDS_QUEUE = Queue.Queue(1)

class CarManager(threading.Thread):
    """
    Car Manager class
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__controller = None
        self.__recorder = None
        self.__analyser = None
        self.__streamer = None
        self.__user_comunicator = None

        # threads
        self.__controller_thread = None
        self.__recorder_thread = None
        self.__analyser_thread = None
        self.__streamer_thread = None
        self.__user_comunicator_thread = None
        self.__rights_thread = None
        self.__process_user_commands_thread = None

        #string containing user rights about controlling the car
        self.__autonomous_rights = None

    def run(self):
        self.__controller = Controller.Controller()
        self.__recorder = Recorder.Recorder()
        self.__analyser = Analyser.Analyser()
        self.__user_comunicator = UserComunicatorServer.UserComunicatorServer(self.get_ip_address())
        self.__streamer = StreamServer.StreamerServer(self.get_ip_address())

        # control car motors thread
        self.__controller_thread = \
            threading.Thread(target=Controller.Controller.send_commands, \
            args=(self.__controller, COMMANDS_QUEUE))
        self.__controller_thread.setDaemon(True)
        self.__controller_thread.start()

        # video capture thread
        self.__recorder_thread = \
            threading.Thread(target=Recorder.Recorder.record, args=(self.__recorder, FRAME_QUEUE))
        self.__recorder_thread.setDaemon(True)
        self.__recorder_thread.start()

        # analyse current frame thread
        self.__analyser_thread = \
            threading.Thread(target=Analyser.Analyser.analyse, \
            args=(self.__analyser, FRAME_QUEUE, AUTONOMOUS_STATES_QUEUE, \
            COMMANDS_QUEUE, ANALYSED_FRAME_QUEUE))
        self.__analyser_thread.setDaemon(True)
        self.__analyser_thread.start()

        # streamer server thread
        self.__streamer_thread = \
            threading.Thread(target=self.__streamer.stream, \
            args=(ANALYSED_FRAME_QUEUE,))
        self.__streamer_thread.setDaemon(True)
        self.__streamer_thread.start()

        # user comunicator server thread
        self.__user_comunicator_thread = \
            threading.Thread(target=self.__user_comunicator.update_user_commands, \
            args=(USER_COMMANDS_QUEUE,))
        self.__user_comunicator_thread.setDaemon(True)
        self.__user_comunicator_thread.start()

        # update user rights thread
        self.__rights_thread = \
            threading.Thread(target=self.__update_user_rights, \
            args=(AUTONOMOUS_STATES_QUEUE,))
        self.__rights_thread.setDaemon(True)
        self.__rights_thread.start()

        # user commands thread
        self.__process_user_commands_thread = \
            threading.Thread(target=self.__process_user_commands, \
            args=(USER_COMMANDS_QUEUE, COMMANDS_QUEUE,))
        self.__process_user_commands_thread.setDaemon(True)
        self.__process_user_commands_thread.start()

    def stop(self):
        """
        Stop the Car Manager
        """
        # send stop event
        self.__controller_thread.is_running = False
        self.__recorder_thread.is_running = False
        self.__analyser_thread.is_running = False
        self.__rights_thread.is_running = False
        self.__process_user_commands_thread.is_running = False
        self.__streamer_thread.is_connected = False
        self.__streamer_thread.is_running = False
        self.__user_comunicator_thread.is_connected = False
        self.__user_comunicator_thread.is_running = False

        # join
        self.__controller_thread.join()
        self.__recorder_thread.join()
        self.__analyser_thread.join()
        self.__rights_thread.join()
        self.__process_user_commands_thread.join()
        self.__streamer_thread.join()
        self.__user_comunicator_thread.join()

    def get_ip_address(self):
        """
        get your current ip address
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]

    def __update_user_rights(self, autonomous_states_queue):
        current_thread = threading.currentThread()
        while getattr(current_thread, 'is_running', True):
            autonomous_states_queue.get(True, None)
            autonomous_states_queue.task_done()

    def __process_user_commands(self, user_commands_queue, commands_queue):
        current_thread = threading.currentThread()
        while getattr(current_thread, 'is_running', True):
            command = user_commands_queue.get(True, None)
            commands_queue.put(command, True, None)
            user_commands_queue.task_done()

# if __name__ == '__main__':
#     AUX = CarManager()
#     AUX.start()
#     time.sleep(10)
#     AUX.stop()
