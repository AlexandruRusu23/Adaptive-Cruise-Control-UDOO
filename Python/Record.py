"""
record module
"""
import threading
import cv2

class Record(threading.Thread):
    """
    record class
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.__camera = None

    def run(self):
        """
        show
        """
        self.__camera = cv2.VideoCapture(1)
        while True:
            ret_val, image = self.__camera.read()
            cv2.imshow('Webcam', image)
            if cv2.waitKey(1) == 27:
                break  # esc to quit
        cv2.destroyAllWindows()

def main():
    """
    main
    """
    record = Record()
    record.start()

if __name__ == '__main__':
    main()
