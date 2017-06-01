"""
Car Manager module
 - responsible for every components that have to run on Car
"""
import time
import Queue
import threading
import socket
import Recorder
import Controller
import StreamerServer
import CommunicatorServer
import DataProviderServer

FRAME_QUEUE = Queue.Queue(1)
COMMANDS_QUEUE = Queue.Queue(1)
USER_COMMANDS_QUEUE = Queue.Queue(1)
CAR_DATA_QUEUE = Queue.Queue(1)

class CarManager(threading.Thread):
    """
    Car Manager class
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__controller = None
        self.__recorder = None
        self.__streamer_server = None
        self.__communicator_server = None
        self.__data_provider_server = None

        self.__is_running = False
        self.__is_running_lock = threading.Lock()

        # threads
        self.__controller_thread = None
        self.__car_data_thread = None
        self.__recorder_thread = None
        self.__streamer_thread = None
        self.__communicator_thread = None
        self.__process_user_commands_thread = None
        self.__data_provider_thread = None

        #string containing user rights about controlling the car
        self.__autonomous_rights = None

    def run(self):
        self.__is_running_lock.acquire()
        self.__is_running = True
        self.__is_running_lock.release()

        self.__controller = Controller.Controller()
        self.__recorder = Recorder.Recorder()
        self.__communicator_server = CommunicatorServer.CommunicatorServer(self.get_ip_address())
        self.__streamer_server = StreamerServer.StreamerServer(self.get_ip_address())
        self.__data_provider_server = DataProviderServer.DataProviderServer(self.get_ip_address())

        # control car motors thread
        self.__controller_thread = \
            threading.Thread(target=Controller.Controller.send_commands, \
            args=(self.__controller, COMMANDS_QUEUE))
        self.__controller_thread.setDaemon(True)
        self.__controller_thread.start()

        # get car data thread
        self.__car_data_thread = \
            threading.Thread(target=Controller.Controller.get_car_data, \
            args=(self.__controller, CAR_DATA_QUEUE))
        self.__car_data_thread.setDaemon(True)
        self.__car_data_thread.start()

        # video capture thread
        self.__recorder_thread = \
            threading.Thread(target=Recorder.Recorder.record, args=(self.__recorder, FRAME_QUEUE))
        self.__recorder_thread.setDaemon(True)
        self.__recorder_thread.start()

        # streamer server thread
        self.__streamer_thread = \
            threading.Thread(target=self.__streamer_server.stream, \
            args=(FRAME_QUEUE,))
        self.__streamer_thread.setDaemon(True)
        self.__streamer_thread.start()

        # comunicator server thread
        self.__communicator_thread = \
            threading.Thread(target=self.__communicator_server.update_user_commands, \
            args=(USER_COMMANDS_QUEUE,))
        self.__communicator_thread.setDaemon(True)
        self.__communicator_thread.start()

        # data provider server thread
        self.__data_provider_thread = \
            threading.Thread(target=self.__data_provider_server.provide, \
            args=(CAR_DATA_QUEUE,))
        self.__data_provider_thread.setDaemon(True)
        self.__data_provider_thread.start()

        # user commands thread
        self.__process_user_commands_thread = \
            threading.Thread(target=self.__process_user_commands, \
            args=(USER_COMMANDS_QUEUE, COMMANDS_QUEUE,))
        self.__process_user_commands_thread.setDaemon(True)
        self.__process_user_commands_thread.start()

        print 'am startat tot'

        while True:
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                self.stop()
                break
            time.sleep(1)

    def stop(self):
        """
        Stop the Car Manager
        """
        # send stop event
        self.__controller_thread.is_running = False
        self.__car_data_thread.is_running = False
        self.__recorder_thread.is_running = False
        self.__process_user_commands_thread.is_running = False
        self.__streamer_thread.is_connected = False
        self.__streamer_thread.is_running = False
        self.__communicator_thread.is_connected = False
        self.__communicator_thread.is_running = False
        self.__data_provider_thread.is_connected = False
        self.__data_provider_thread.is_running = False
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

        # join
        self.__controller_thread.join()
        print '[Controller] Thread stopped.'
        self.__car_data_thread.join()
        print '[CarData] Thread stopped.'
        self.__recorder_thread.join()
        print '[Recorder] Thread stopped.'
        self.__process_user_commands_thread.join()
        print '[UserCommands] Thread stopped.'
        self.__streamer_thread.join()
        print '[Streamer] Thread stopped.'
        self.__communicator_thread.join()
        print '[UserComunicator] Thread stopped.'
        self.__data_provider_thread.join()
        print '[DataProvider] Thread stopped.'

    def get_ip_address(self):
        """
        get your current ip address
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        output = sock.getsockname()[0]
        sock.close()
        return output

    def __process_user_commands(self, user_commands_queue, commands_queue):
        current_thread = threading.currentThread()
        while getattr(current_thread, 'is_running', True):
            command = user_commands_queue.get(True, None)
            if 'CLOSE' in str(command):
                self.__is_running_lock.acquire()
                self.__is_running = False
                self.__is_running_lock.release()
            else:
                commands_queue.put(str(command), True, None)
            user_commands_queue.task_done()
        print '[User_Commands] Thread has stopped.'
