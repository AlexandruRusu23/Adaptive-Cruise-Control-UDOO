# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Controller.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(660, 699)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.distance_buttons_layout = QtGui.QVBoxLayout()
        self.distance_buttons_layout.setObjectName(_fromUtf8("distance_buttons_layout"))
        self.increase_distance_button = QtGui.QPushButton(self.centralwidget)
        self.increase_distance_button.setObjectName(_fromUtf8("increase_distance_button"))
        self.distance_buttons_layout.addWidget(self.increase_distance_button)
        self.decrease_distance_button = QtGui.QPushButton(self.centralwidget)
        self.decrease_distance_button.setObjectName(_fromUtf8("decrease_distance_button"))
        self.distance_buttons_layout.addWidget(self.decrease_distance_button)
        self.gridLayout.addLayout(self.distance_buttons_layout, 1, 0, 3, 1)
        self.streamer_image_layout = QtGui.QVBoxLayout()
        self.streamer_image_layout.setObjectName(_fromUtf8("streamer_image_layout"))
        self.streamer_image_view = QtGui.QGraphicsView(self.centralwidget)
        self.streamer_image_view.setMinimumSize(QtCore.QSize(640, 480))
        self.streamer_image_view.setObjectName(_fromUtf8("streamer_image_view"))
        self.streamer_image_layout.addWidget(self.streamer_image_view)
        self.gridLayout.addLayout(self.streamer_image_layout, 0, 0, 1, 6)
        self.speed_buttons_layout = QtGui.QVBoxLayout()
        self.speed_buttons_layout.setObjectName(_fromUtf8("speed_buttons_layout"))
        self.speed_up_button = QtGui.QPushButton(self.centralwidget)
        self.speed_up_button.setObjectName(_fromUtf8("speed_up_button"))
        self.speed_buttons_layout.addWidget(self.speed_up_button)
        self.speed_down_button = QtGui.QPushButton(self.centralwidget)
        self.speed_down_button.setObjectName(_fromUtf8("speed_down_button"))
        self.speed_buttons_layout.addWidget(self.speed_down_button)
        self.brake_button = QtGui.QPushButton(self.centralwidget)
        self.brake_button.setObjectName(_fromUtf8("brake_button"))
        self.speed_buttons_layout.addWidget(self.brake_button)
        self.gridLayout.addLayout(self.speed_buttons_layout, 1, 5, 3, 1)
        self.states_layout = QtGui.QFormLayout()
        self.states_layout.setObjectName(_fromUtf8("states_layout"))
        self.speed_label = QtGui.QLabel(self.centralwidget)
        self.speed_label.setObjectName(_fromUtf8("speed_label"))
        self.states_layout.setWidget(0, QtGui.QFormLayout.LabelRole, self.speed_label)
        self.speed_text = QtGui.QLineEdit(self.centralwidget)
        self.speed_text.setReadOnly(True)
        self.speed_text.setObjectName(_fromUtf8("speed_text"))
        self.states_layout.setWidget(0, QtGui.QFormLayout.FieldRole, self.speed_text)
        self.preferred_speed_label = QtGui.QLabel(self.centralwidget)
        self.preferred_speed_label.setObjectName(_fromUtf8("preferred_speed_label"))
        self.states_layout.setWidget(1, QtGui.QFormLayout.LabelRole, self.preferred_speed_label)
        self.preferred_speed_text = QtGui.QLineEdit(self.centralwidget)
        self.preferred_speed_text.setReadOnly(True)
        self.preferred_speed_text.setObjectName(_fromUtf8("preferred_speed_text"))
        self.states_layout.setWidget(1, QtGui.QFormLayout.FieldRole, self.preferred_speed_text)
        self.cruise_distance_label = QtGui.QLabel(self.centralwidget)
        self.cruise_distance_label.setObjectName(_fromUtf8("cruise_distance_label"))
        self.states_layout.setWidget(2, QtGui.QFormLayout.LabelRole, self.cruise_distance_label)
        self.cruise_distance_text = QtGui.QLineEdit(self.centralwidget)
        self.cruise_distance_text.setReadOnly(True)
        self.cruise_distance_text.setObjectName(_fromUtf8("cruise_distance_text"))
        self.states_layout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cruise_distance_text)
        self.detection_label = QtGui.QLabel(self.centralwidget)
        self.detection_label.setObjectName(_fromUtf8("detection_label"))
        self.states_layout.setWidget(3, QtGui.QFormLayout.LabelRole, self.detection_label)
        self.detection_text = QtGui.QLineEdit(self.centralwidget)
        self.detection_text.setReadOnly(True)
        self.detection_text.setObjectName(_fromUtf8("detection_text"))
        self.states_layout.setWidget(3, QtGui.QFormLayout.FieldRole, self.detection_text)
        self.command_label = QtGui.QLabel(self.centralwidget)
        self.command_label.setObjectName(_fromUtf8("command_label"))
        self.states_layout.setWidget(4, QtGui.QFormLayout.LabelRole, self.command_label)
        self.command_text = QtGui.QLineEdit(self.centralwidget)
        self.command_text.setReadOnly(True)
        self.command_text.setObjectName(_fromUtf8("command_text"))
        self.states_layout.setWidget(4, QtGui.QFormLayout.FieldRole, self.command_text)
        self.gridLayout.addLayout(self.states_layout, 1, 1, 3, 4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Adaptive Cruise Control - RS Lang", None))
        self.increase_distance_button.setText(_translate("MainWindow", "Increase Distance", None))
        self.decrease_distance_button.setText(_translate("MainWindow", "Decrease Distance", None))
        self.speed_up_button.setText(_translate("MainWindow", "Speed Up", None))
        self.speed_down_button.setText(_translate("MainWindow", "Speed Down", None))
        self.brake_button.setText(_translate("MainWindow", "Brake", None))
        self.speed_label.setText(_translate("MainWindow", "Speed", None))
        self.preferred_speed_label.setText(_translate("MainWindow", "Preferred Speed", None))
        self.cruise_distance_label.setText(_translate("MainWindow", "Cruise Distance", None))
        self.detection_label.setText(_translate("MainWindow", "Detection", None))
        self.command_label.setText(_translate("MainWindow", "Command", None))

