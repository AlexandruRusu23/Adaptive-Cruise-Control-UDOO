"""
Controller module
In this module is provided a class that will comunicate with the
remote application in order to configure the Car states.
"""
import threading
import socket
import SerialManager

class ControllerServer(threading.Thread):
    """
    Controller class
    Is has to comunicate with the remote app to send the setup commands
    to Car using SerialManager
    """
    def __init__(self, hostname='192.168.0.106', port=32656):
        threading.Thread.__init__(self)
        self.__serial_manager = None
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__server_address = (hostname, port)
        self.__socket = None

    def run(self):
        self.__is_running = True
        self.__serial_manager = SerialManager.SerialManager('/dev/ttyACM0', 9600)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_address)
        # We want only one client
        self.__socket.listen(1)
        # Listen to infinite connection if Client disconnect
        while True:
            connection, client_address = self.__socket.accept()
            print client_address
            try:
                while True:
                    data = connection.recv(1024) #valid
                    if data:
                        commands = []
                        commands.append(data)
                        self.__serial_manager.set_controller_commands(commands)
                        self.__serial_manager.execute_commands()
                    else:
                        break

                    self.__is_running_lock.acquire()
                    condition = self.__is_running
                    self.__is_running_lock.release()

                    if bool(condition) is False:
                        break

            finally:
                # Clean up the connection
                connection.close()
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()

            if bool(condition) is False:
                break

    def stop(self):
        """
        Stop the Controller Server
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()
