"""
Main file for the Application which runs on the Car
"""
import threading
import time
import CarManager

class CarMain(threading.Thread):
    """
    CarMain class
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.__car_manager = None
        self.__is_running = False
        self.__is_running_lock = threading.Lock()

    def run(self):
        """
        Launch the application
        """
        self.__is_running_lock.acquire()
        self.__is_running = True
        self.__is_running_lock.release()
        self.__car_manager = CarManager.CarManager()
        self.__car_manager.start()
        while True:
            self.__is_running_lock.acquire()
            condition = self.__is_running
            self.__is_running_lock.release()

            if bool(condition) is False:
                self.__car_manager.stop()
                break
            time.sleep(1)

        self.__car_manager.join()
        print '[CarApp] The main thread has stopped.'

    def stop(self):
        """
        Stop the application
        """
        self.__is_running_lock.acquire()
        self.__is_running = False
        self.__is_running_lock.release()

if __name__ == '__main__':
    try:
        CAR_MAIN = CarMain()
        CAR_MAIN.start()
        while 'Exit' not in str(input('[CarMain] $ ')):
            time.sleep(1)
        CAR_MAIN.stop()
        CAR_MAIN.join()
    except KeyboardInterrupt:
        CAR_MAIN.stop()
        CAR_MAIN.join()
