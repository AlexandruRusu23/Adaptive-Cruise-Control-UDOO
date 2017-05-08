"""
Streamer module
This module has to provide the live from the camera to the
remote application
"""
import threading
import socket
import sys

class StreamerServer(threading.Thread):
    """
    Streamer class
    """
    def __init__(self, host='192.168.0.106', port=8089):
        threading.Thread.__init__(self)
        self.__socket = None
        self.__server_adress = (host, port)
        self.__data_to_send = None
        self.__data_to_send_lock = threading.Lock()
        self.__is_running = False
        self.__is_running_lock = threading.Lock()
        self.__is_connected = False
        self.__is_connected_lock = threading.Lock()

    def run(self):
        self.__is_running = True
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__server_adress)
        # We want only one client
        self.__socket.listen(1)
        while True:
            print >>sys.stderr, 'waiting for a connection', self.__server_adress
            connection, client_address = self.__socket.accept()
            try:
                print >>sys.stderr, 'connection from', client_address
                self.__is_connected = True
                while True:
                    self.__data_to_send_lock.acquire()
                    data_to_send = self.__data_to_send
                    self.__data_to_send_lock.release()

                    if data_to_send is not None:
                        connection.send(str(len(data_to_send)).ljust(4096))
                        connection.send(data_to_send)

                    self.__is_connected_lock.acquire()
                    condition = self.__is_connected
                    self.__is_connected_lock.release()
                    if bool(condition) is False:
                        break
            except KeyboardInterrupt:
                self.stop()

            finally:
                connection.close()
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()
            if bool(condition) is False:
                connection.close()
                break

    def stop_streamer(self):
        """
        stop the connection between server and client
        """
        self.__is_connected_lock.acquire()
        self.__is_connected = False
        self.__is_connected_lock.release()

    def stop(self):
        """
        Stop the Streamer Server
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()
        self.stop_streamer()

    def is_connected(self):
        """
        check if a connection has been established
        """
        self.__is_connected_lock.acquire()
        output = self.__is_connected
        self.__is_connected_lock.release()
        return output

    def set_encrypted_frame(self, encrypted_frame):
        """
        set the frame to be send to client
        """
        self.__data_to_send_lock.acquire()
        self.__data_to_send = encrypted_frame
        self.__data_to_send_lock.release()
