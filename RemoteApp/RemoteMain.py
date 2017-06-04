"""
Main for Remote App
"""
import sys
import threading
import numpy
import cv2
import Queue
from PyQt4 import QtGui, QtCore

import CommunicatorClient
import DataProviderClient
import StreamerClient
import Analyser

FRAME_QUEUE = Queue.Queue(1)
ANALYSED_FRAME_QUEUE = Queue.Queue(1)
COMMANDS_QUEUE = Queue.Queue(1)
USER_COMMANDS_QUEUE = Queue.Queue(1)
AUTONOMOUS_STATES_QUEUE = Queue.Queue(1)
CAR_DATA_QUEUE = Queue.Queue(1)
CAR_STATES_QUEUE = Queue.Queue(1)

# string resources
CMD_GO_FORWARD = '1/1/'
CMD_INCREASE_SPEED = '1/2/'
CMD_DECREASE_SPEED = '2/'
CMD_BRAKE = '3/'
CMD_GO_LEFT = '4/'
CMD_GO_RIGHT = '5/'
CMD_GO_BACKWARD = '6/'

CSQ_CRUISE_DISTANCE = 'CRUISE_DISTANCE'
CSQ_CRUISE_SPEED = 'CRUISE_SPEED'
CSQ_CRUISE_PREFFERED_SPEED = 'CRUISE_PREF_SPEED'

try:
    #we want to use the same name form
    FROM_UTF8 = QtCore.QString.fromUtf8
except AttributeError:
    def from_utf8(string_name):
        """
        from utf8 alternative
        """
        return string_name
    FROM_UTF8 = from_utf8

try:
    ENCODING = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, ENCODING)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class OwnImageWidget(QtGui.QWidget):
    """
    own class for image widget (adapted for numpy arrays)
    """
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def set_image(self, image):
        """
        set the current image to be showed
        """
        self.image = image
        image_size = image.size()
        self.setMinimumSize(image_size)
        self.update()

    #overwritten function from Qt Library
    def paintEvent(self, event):
        """
        paint event
        """
        qpainter = QtGui.QPainter()
        qpainter.begin(self)
        if self.image:
            qpainter.drawImage(QtCore.QPoint(0, 0), self.image)
        qpainter.end()

class RemoteMain(object):
    """
    Remote Main Class
    """

    def __init__(self, server_host):
        """
        All components needed for UI
        * declared first in __init__ as None
        """
        self.__host = server_host

        self.__streamer_client = None
        self.__communicator_client = None
        self.__data_provider_client = None
        self.__analyser = None

        self.__streamer_client_thread = None
        self.__communicator_client_thread = None
        self.__data_provider_client_thread = None
        self.__analyser_thread = None

        self.update_frame_timer = None
        self.update_car_data_timer = None
        self.superviser_timer = None

        self.__current_command = ''

        self.__acc_activated = False
        self.__cruise_watch_area = 0
        self.__cruise_speed = 0
        self.__cruise_preffered_speed = 0

        self.window_width = None
        self.window_height = None
        self.centralwidget = None
        self.grid_layout = None
        self.distance_buttons_layout = None
        self.acc_activate_button = None
        self.increase_distance_button = None
        self.decrease_distance_button = None
        self.streamer_image_layout = None
        self.streamer_image_view = None
        self.speed_buttons_layout = None
        self.speed_up_button = None
        self.speed_down_button = None
        self.brake_button = None
        self.states_layout = None
        self.speed_label = None
        self.speed_text = None
        self.preferred_speed_label = None
        self.preferred_speed_text = None
        self.cruise_distance_label = None
        self.cruise_distance_text = None
        self.detection_label = None
        self.detection_text = None
        self.command_label = None
        self.command_text = None
        self.statusbar = None

    def setup_ui(self, main_window):
        """
        Setup UI components
        """
        self.__streamer_client = StreamerClient.StreamerClient(self.__host)
        self.__communicator_client = CommunicatorClient.CommunicatorClient(self.__host)
        self.__data_provider_client = DataProviderClient.DataProviderClient(self.__host)
        self.__analyser = Analyser.Analyser()

        main_window.setObjectName(FROM_UTF8("main_window"))
        main_window.resize(660, 700)
        main_window.keyPressEvent = self.key_press_event
        main_window.closeEvent = self.close_event
        self.centralwidget = QtGui.QWidget(main_window)
        self.centralwidget.setObjectName(FROM_UTF8("centralwidget"))
        self.grid_layout = QtGui.QGridLayout(self.centralwidget)
        self.grid_layout.setObjectName(FROM_UTF8("grid_layout"))
        self.distance_buttons_layout = QtGui.QVBoxLayout()
        self.distance_buttons_layout.setObjectName(FROM_UTF8("distance_buttons_layout"))
        self.acc_activate_button = QtGui.QPushButton(self.centralwidget)
        self.acc_activate_button.setObjectName(FROM_UTF8("acc_activate_button"))
        self.distance_buttons_layout.addWidget(self.acc_activate_button)
        self.increase_distance_button = QtGui.QPushButton(self.centralwidget)
        self.increase_distance_button.setObjectName(FROM_UTF8("increase_distance_button"))
        self.distance_buttons_layout.addWidget(self.increase_distance_button)
        self.decrease_distance_button = QtGui.QPushButton(self.centralwidget)
        self.decrease_distance_button.setObjectName(FROM_UTF8("decrease_distance_button"))
        self.distance_buttons_layout.addWidget(self.decrease_distance_button)
        self.grid_layout.addLayout(self.distance_buttons_layout, 1, 0, 3, 1)
        self.streamer_image_layout = QtGui.QVBoxLayout()
        self.streamer_image_layout.setObjectName(FROM_UTF8("streamer_image_layout"))
        self.streamer_image_view = QtGui.QLabel(self.centralwidget)
        self.streamer_image_view = OwnImageWidget(self.streamer_image_view)
        self.streamer_image_view.setMinimumSize(QtCore.QSize(640, 480))
        self.streamer_image_view.setObjectName(FROM_UTF8("streamer_image_view"))
        self.streamer_image_layout.addWidget(self.streamer_image_view)
        self.grid_layout.addLayout(self.streamer_image_layout, 0, 0, 1, 6)
        self.speed_buttons_layout = QtGui.QVBoxLayout()
        self.speed_buttons_layout.setObjectName(FROM_UTF8("speed_buttons_layout"))
        self.speed_up_button = QtGui.QPushButton(self.centralwidget)
        self.speed_up_button.setObjectName(FROM_UTF8("speed_up_button"))
        self.speed_buttons_layout.addWidget(self.speed_up_button)
        self.speed_down_button = QtGui.QPushButton(self.centralwidget)
        self.speed_down_button.setObjectName(FROM_UTF8("speed_down_button"))
        self.speed_buttons_layout.addWidget(self.speed_down_button)
        self.brake_button = QtGui.QPushButton(self.centralwidget)
        self.brake_button.setObjectName(FROM_UTF8("brake_button"))
        self.speed_buttons_layout.addWidget(self.brake_button)
        self.grid_layout.addLayout(self.speed_buttons_layout, 1, 5, 3, 1)
        self.states_layout = QtGui.QFormLayout()
        self.states_layout.setObjectName(FROM_UTF8("states_layout"))
        self.speed_label = QtGui.QLabel(self.centralwidget)
        self.speed_label.setObjectName(FROM_UTF8("speed_label"))
        self.states_layout.setWidget(0, QtGui.QFormLayout.LabelRole, self.speed_label)
        self.speed_text = QtGui.QLineEdit(self.centralwidget)
        self.speed_text.setReadOnly(True)
        self.speed_text.setObjectName(FROM_UTF8("speed_text"))
        self.states_layout.setWidget(0, QtGui.QFormLayout.FieldRole, self.speed_text)
        self.preferred_speed_label = QtGui.QLabel(self.centralwidget)
        self.preferred_speed_label.setObjectName(FROM_UTF8("preferred_speed_label"))
        self.states_layout.setWidget(1, QtGui.QFormLayout.LabelRole, self.preferred_speed_label)
        self.preferred_speed_text = QtGui.QLineEdit(self.centralwidget)
        self.preferred_speed_text.setReadOnly(True)
        self.preferred_speed_text.setObjectName(FROM_UTF8("preferred_speed_text"))
        self.states_layout.setWidget(1, QtGui.QFormLayout.FieldRole, self.preferred_speed_text)
        self.cruise_distance_label = QtGui.QLabel(self.centralwidget)
        self.cruise_distance_label.setObjectName(FROM_UTF8("cruise_distance_label"))
        self.states_layout.setWidget(2, QtGui.QFormLayout.LabelRole, self.cruise_distance_label)
        self.cruise_distance_text = QtGui.QLineEdit(self.centralwidget)
        self.cruise_distance_text.setReadOnly(True)
        self.cruise_distance_text.setObjectName(FROM_UTF8("cruise_distance_text"))
        self.states_layout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cruise_distance_text)
        self.detection_label = QtGui.QLabel(self.centralwidget)
        self.detection_label.setObjectName(FROM_UTF8("detection_label"))
        self.states_layout.setWidget(3, QtGui.QFormLayout.LabelRole, self.detection_label)
        self.detection_text = QtGui.QLineEdit(self.centralwidget)
        self.detection_text.setReadOnly(True)
        self.detection_text.setObjectName(FROM_UTF8("detection_text"))
        self.states_layout.setWidget(3, QtGui.QFormLayout.FieldRole, self.detection_text)
        self.command_label = QtGui.QLabel(self.centralwidget)
        self.command_label.setObjectName(FROM_UTF8("command_label"))
        self.states_layout.setWidget(4, QtGui.QFormLayout.LabelRole, self.command_label)
        self.command_text = QtGui.QLineEdit(self.centralwidget)
        self.command_text.setReadOnly(True)
        self.command_text.setObjectName(FROM_UTF8("command_text"))
        self.states_layout.setWidget(4, QtGui.QFormLayout.FieldRole, self.command_text)
        self.grid_layout.addLayout(self.states_layout, 1, 1, 3, 4)
        main_window.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(main_window)
        self.statusbar.setObjectName(FROM_UTF8("statusbar"))
        main_window.setStatusBar(self.statusbar)

        # receive frames thread
        self.__streamer_client_thread = \
            threading.Thread(target=StreamerClient.StreamerClient.receive_stream, \
            args=(self.__streamer_client, FRAME_QUEUE))
        self.__streamer_client_thread.setDaemon(True)
        self.__streamer_client_thread.start()

        # send commands to car thread
        self.__communicator_client_thread = \
            threading.Thread(target=CommunicatorClient.CommunicatorClient.send_commands, \
            args=(self.__communicator_client, COMMANDS_QUEUE))
        self.__communicator_client_thread.setDaemon(True)
        self.__communicator_client_thread.start()

        # receive data about the car thread
        self.__data_provider_client_thread = \
            threading.Thread(target=DataProviderClient.DataProviderClient.receive_car_data, \
            args=(self.__data_provider_client, CAR_DATA_QUEUE))
        self.__data_provider_client_thread.setDaemon(True)
        self.__data_provider_client_thread.start()

        # analyse every frame and take decisions thread
        self.__analyser_thread = \
            threading.Thread(target=Analyser.Analyser.analyse, \
            args=(self.__analyser, FRAME_QUEUE, ANALYSED_FRAME_QUEUE, AUTONOMOUS_STATES_QUEUE, \
            COMMANDS_QUEUE, CAR_STATES_QUEUE,))
        self.__analyser_thread.setDaemon(True)
        self.__analyser_thread.start()
        self.__analyser_thread.is_analysing = self.__acc_activated

        # update frames thread
        self.update_frame_timer = QtCore.QTimer(self.streamer_image_layout)
        self.update_frame_timer.timeout.connect(self.__update_frame)
        self.update_frame_timer.start(10)

        # update car data thread
        self.update_car_data_timer = QtCore.QTimer(self.states_layout)
        self.update_car_data_timer.timeout.connect(self.__update_car_data)
        self.update_car_data_timer.start(200)

        # supervise the user settings and sync entire app thread
        self.superviser_timer = QtCore.QTimer(self.centralwidget)
        self.superviser_timer.timeout.connect(self.__superviser_thread)
        self.superviser_timer.start(100)

        self.window_width = self.streamer_image_view.frameSize().width()
        self.window_height = self.streamer_image_view.frameSize().height()

        self.speed_up_button.clicked.connect(self.__speed_up_button_clicked)
        self.speed_down_button.clicked.connect(self.__speed_down_button_clicked)
        self.brake_button.clicked.connect(self.__brake_button_clicked)
        self.increase_distance_button.clicked.connect(self.__increase_distance_btn_clicked)
        self.decrease_distance_button.clicked.connect(self.__decrease_distance_btn_clicked)
        self.acc_activate_button.clicked.connect(self.__acc_activate_button_clicked)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        """
        UI retranslations
        """
        main_window.setWindowTitle(\
            _translate("main_window", "Adaptive Cruise Control - RS Lang", None))
        self.acc_activate_button.setText(_translate("main_window", "ACC", None))
        self.increase_distance_button.setText(_translate("main_window", "Increase Distance", None))
        self.decrease_distance_button.setText(_translate("main_window", "Decrease Distance", None))
        self.speed_up_button.setText(_translate("main_window", "Speed Up", None))
        self.speed_down_button.setText(_translate("main_window", "Speed Down", None))
        self.brake_button.setText(_translate("main_window", "Brake", None))
        self.speed_label.setText(_translate("main_window", "Speed", None))
        self.preferred_speed_label.setText(_translate("main_window", "Preferred Speed", None))
        self.cruise_distance_label.setText(_translate("main_window", "Cruise Distance", None))
        self.detection_label.setText(_translate("main_window", "Detection", None))
        self.command_label.setText(_translate("main_window", "Command", None))

    def __acc_activate_button_clicked(self):
        self.__acc_activated = not self.__acc_activated
        self.__analyser_thread.is_analysing = self.__acc_activated

    def __speed_up_button_clicked(self):
        if self.__cruise_preffered_speed < 250:
            if self.__cruise_preffered_speed < 100:
                self.__cruise_preffered_speed = 100
            else:
                self.__cruise_preffered_speed = self.__cruise_preffered_speed + 10

    def __speed_down_button_clicked(self):
        if self.__cruise_speed == 0:
            self.__cruise_preffered_speed = 0
        if self.__cruise_preffered_speed > 100:
            self.__cruise_preffered_speed = self.__cruise_preffered_speed - 10
        else:
            self.__cruise_preffered_speed = 0

    def __brake_button_clicked(self):
        self.__cruise_preffered_speed = 0
        print 'brake'

    def __increase_distance_btn_clicked(self):
        if self.__cruise_watch_area < 4:
            self.__cruise_watch_area = self.__cruise_watch_area + 1
        print 'increase ' + str(self.__cruise_watch_area)

    def __decrease_distance_btn_clicked(self):
        if self.__cruise_watch_area > 0:
            self.__cruise_watch_area = self.__cruise_watch_area - 1
        print 'decrease ' + str(self.__cruise_watch_area)

    def key_press_event(self, event):
        """
        key press
        """
        key = event.key()

        if key == QtCore.Qt.Key_Escape:
            sys.exit()
        elif key == QtCore.Qt.Key_W:
            print 'W'
            COMMANDS_QUEUE.put(CMD_INCREASE_SPEED, True, None)
        elif key == QtCore.Qt.Key_A:
            print 'A'
            COMMANDS_QUEUE.put(CMD_GO_LEFT, True, None)
        elif key == QtCore.Qt.Key_S:
            print 'S'
            COMMANDS_QUEUE.put(CMD_DECREASE_SPEED, True, None)
        elif key == QtCore.Qt.Key_D:
            print 'D'
            COMMANDS_QUEUE.put(CMD_GO_RIGHT, True, None)
        elif key == QtCore.Qt.Key_M:
            print 'M'
            COMMANDS_QUEUE.put(CMD_BRAKE, True, None)
        elif key == QtCore.Qt.Key_R:
            print 'R'
            COMMANDS_QUEUE.put(CMD_GO_BACKWARD, True, None)
        elif key == QtCore.Qt.Key_I:
            print 'I'
        elif key == QtCore.Qt.Key_O:
            print 'O'

    def __update_frame(self):
        string_data = ANALYSED_FRAME_QUEUE.get(True, None)
        data = numpy.fromstring(string_data, dtype='uint8')
        cv_image = cv2.imdecode(data, 1)
        if cv_image is not None:
            img_height, img_width, img_colors = cv_image.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1

            cv_image = \
                cv2.resize(cv_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            height, width, bpc = cv_image.shape
            bpl = bpc * width
            image = QtGui.QImage(cv_image.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.streamer_image_view.set_image(image)
        ANALYSED_FRAME_QUEUE.task_done()

    def __update_car_data(self):
        try:
            car_data = CAR_DATA_QUEUE.get(False)
        except Queue.Empty:
            return
        car_data = car_data.split(';')
        for elem in car_data:
            current_state = elem.split(',')
            if len(current_state) > 1:
                if 'ACTION' in current_state[0]:
                    self.__current_command = str(current_state[1])
                elif 'SPEED' in current_state[0]:
                    self.__cruise_speed = int(current_state[1])
        CAR_DATA_QUEUE.task_done()

    def __superviser_thread(self):
        if bool(self.__acc_activated) is False:
            self.acc_activate_button.setStyleSheet("background-color: red")
        else:
            self.acc_activate_button.setStyleSheet("background-color: green")

        self.speed_text.setText(_translate("main_window", str(self.__cruise_speed), None))
        self.command_text.setText(_translate("main_window", str(self.__current_command), None))
        self.preferred_speed_text.setText(_translate("main_window", \
            str(self.__cruise_preffered_speed), None))

        cruise_distance = self.__cruise_watch_area * 5
        self.cruise_distance_text.setText(_translate("main_window", \
            str(cruise_distance) + ' cm', None))

        preffered_speed = CSQ_CRUISE_PREFFERED_SPEED +','+ str(self.__cruise_preffered_speed) + ';'
        speed = CSQ_CRUISE_SPEED +','+ str(self.__cruise_speed) + ';'
        speed = speed + preffered_speed
        cruise_distance = CSQ_CRUISE_DISTANCE + ',' + str(self.__cruise_watch_area) + ';'
        cruise_distance = cruise_distance + speed
        try:
            CAR_STATES_QUEUE.put(cruise_distance, False)
        except Queue.Full:
            pass

    def close_event(self, event):
        """
        close event
        """
        self.update_frame_timer.stop()
        self.update_car_data_timer.stop()
        self.superviser_timer.stop()
        event.accept()

if __name__ == "__main__":
    MAIN_APP = QtGui.QApplication(sys.argv)
    MAIN_WINDOW = QtGui.QMainWindow()
    if len(sys.argv) > 1:
        USER_INTERFACE = RemoteMain(str(sys.argv[1]))
        USER_INTERFACE.setup_ui(MAIN_WINDOW)
        MAIN_WINDOW.show()
        sys.exit(MAIN_APP.exec_())
    else:
        print 'No ip given'
