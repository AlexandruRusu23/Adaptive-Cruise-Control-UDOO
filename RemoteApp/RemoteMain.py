"""
Main for Remote App
"""
import sys
from PyQt4 import QtCore, QtGui

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


class RemoteMain(object):
    """
    Remote Main Class
    """
    def __init__(self):
        """
        All components needed for UI
        * declare first in __init__ as None
        """
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

    def setup_ui(self, main_window):
        """
        Setup UI components
        """
        main_window.setObjectName(FROM_UTF8("main_window"))
        main_window.resize(660, 700)
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
        self.streamer_image_view = QtGui.QGraphicsView(self.centralwidget)
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

if __name__ == "__main__":
    MAIN_APP = QtGui.QApplication(sys.argv)
    MAIN_WINDOW = QtGui.QMainWindow()
    USER_INTERFACE = RemoteMain()
    USER_INTERFACE.setup_ui(MAIN_WINDOW)
    MAIN_WINDOW.show()
    sys.exit(MAIN_APP.exec_())
