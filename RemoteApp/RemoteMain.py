"""
Main for Remote App
"""
import sys
import threading
import cv2
from PyQt4 import QtCore, QtGui
import ControllerClient
import StreamerClient

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
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()

class RemoteMain(object):
    """
    Remote Main Class
    """
    def __init__(self):
        """
        All components needed for UI
        * declare first in __init__ as None
        """
        self.__controller = ControllerClient.ControllerClient()
        self.__streamer = StreamerClient.StreamerClient()
        self.__streamer_image_thread = None

        self.window_width = None
        self.window_height = None

        self.centralwidget = None
        self.grid_layout = None
        self.distance_buttons_layout = None
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
        self.timer = None

    def setup_ui(self, main_window):
        """
        Setup UI components
        """
        main_window.setObjectName(FROM_UTF8("main_window"))
        main_window.resize(660, 700)
        main_window.keyPressEvent = self.key_press_event
        self.centralwidget = QtGui.QWidget(main_window)
        self.centralwidget.setObjectName(FROM_UTF8("centralwidget"))
        self.grid_layout = QtGui.QGridLayout(self.centralwidget)
        self.grid_layout.setObjectName(FROM_UTF8("grid_layout"))
        self.distance_buttons_layout = QtGui.QVBoxLayout()
        self.distance_buttons_layout.setObjectName(FROM_UTF8("distance_buttons_layout"))
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

        self.timer = QtCore.QTimer(self.centralwidget)
        self.timer.timeout.connect(self.__update_frame)
        self.timer.start(1)

        self.window_width = self.streamer_image_view.frameSize().width()
        self.window_height = self.streamer_image_view.frameSize().height()

        self.speed_up_button.clicked.connect(self.__speed_up_button_clicked)
        self.speed_down_button.clicked.connect(self.__speed_down_button_clicked)
        self.brake_button.clicked.connect(self.__brake_button_clicked)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        """
        UI retranslations
        """
        main_window.setWindowTitle(\
            _translate("main_window", "Adaptive Cruise Control - RS Lang", None))
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

    def __speed_up_button_clicked(self):
        self.command_text.setText(_translate("main_window", "Speed increased", None))
        self.__send_command('SPEED_UP')

    def __speed_down_button_clicked(self):
        self.command_text.setText(_translate("main_window", "Speed decreased", None))
        self.__send_command('SPEED_DOWN')

    def __brake_button_clicked(self):
        self.command_text.setText(_translate("main_window", "Brake activated", None))
        self.__send_command('BRAKE')

    def __send_command(self, command_type):
        if command_type == 'SPEED_UP':
            self.__controller.execute_command('SPEED_UP')
        elif command_type == 'SPEED_DOWN':
            self.__controller.execute_command('SPEED_DOWN')
        elif command_type == 'BRAKE':
            self.__controller.execute_command('BRAKE')

    def key_press_event(self, event):
        """
        key press
        """
        key = event.key()
        if chr(key) == 'W':
            self.__controller.execute_command('SPEED_UP')
        if chr(key) == 'A':
            self.__controller.execute_command('GO_LEFT')
        if chr(key) == 'S':
            self.__controller.execute_command('SPEED_DOWN')
        if chr(key) == 'D':
            self.__controller.execute_command('GO_RIGHT')
        if chr(key) == 'M':
            self.__controller.execute_command('BRAKE')
        if chr(key) == 'R':
            self.__controller.execute_command('REAR')
        if chr(key) == 'T':
            self.__streamer.start()
            # self.__streamer_image_thread = \
            #     threading.Thread(target=self.__show_streamer_image, args=())
            # self.__streamer_image_thread.start()

    def __update_frame(self):
        cv_image = self.__streamer.get_frame()
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
            self.streamer_image_view.setImage(image)

if __name__ == "__main__":
    MAIN_APP = QtGui.QApplication(sys.argv)
    MAIN_WINDOW = QtGui.QMainWindow()
    USER_INTERFACE = RemoteMain()
    USER_INTERFACE.setup_ui(MAIN_WINDOW)
    MAIN_WINDOW.show()
    sys.exit(MAIN_APP.exec_())