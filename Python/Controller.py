"""
Controller
"""
from PyQt4 import QtCore, QtGui
import socket
import sys
import time


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

class Controller(object):
    """
    Controller
    """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        self.server_address = ('192.168.0.105', 32656)

    def connect(self):
        print >>sys.stderr, 'connecting to %s port %s' % self.server_address
        self.sock.connect(self.server_address)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        MainWindow.keyPressEvent = self.key_press_event
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.speed_up_button = QtGui.QPushButton(self.centralwidget)
        self.speed_up_button.setObjectName(_fromUtf8("speed_up_button"))
        self.gridLayout.addWidget(self.speed_up_button, 0, 1, 1, 1)
        self.left_button = QtGui.QPushButton(self.centralwidget)
        self.left_button.setObjectName(_fromUtf8("left_button"))
        self.gridLayout.addWidget(self.left_button, 1, 0, 1, 1)
        self.speed_down_button = QtGui.QPushButton(self.centralwidget)
        self.speed_down_button.setObjectName(_fromUtf8("speed_down_button"))
        self.gridLayout.addWidget(self.speed_down_button, 1, 1, 1, 1)
        self.right_button = QtGui.QPushButton(self.centralwidget)
        self.right_button.setObjectName(_fromUtf8("right_button"))
        self.gridLayout.addWidget(self.right_button, 1, 2, 1, 1)
        self.rear_button = QtGui.QPushButton(self.centralwidget)
        self.rear_button.setObjectName(_fromUtf8("rear_button"))
        self.gridLayout.addWidget(self.rear_button, 2, 1, 1, 1)
        self.brake_button = QtGui.QPushButton(self.centralwidget)
        self.brake_button.setObjectName(_fromUtf8("brake_button"))
        self.gridLayout.addWidget(self.brake_button, 3, 0, 1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.speed_up_button.clicked.connect(self.__speed_up)
        self.speed_down_button.clicked.connect(self.__speed_down)
        self.left_button.clicked.connect(self.__go_left)
        self.right_button.clicked.connect(self.__go_right)
        self.brake_button.clicked.connect(self.__brake)
        self.rear_button.clicked.connect(self.__rear)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.speed_up_button.setText(_translate("MainWindow", "Speed Up", None))
        self.left_button.setText(_translate("MainWindow", "Left", None))
        self.speed_down_button.setText(_translate("MainWindow", "Speed Down", None))
        self.right_button.setText(_translate("MainWindow", "Right", None))
        self.rear_button.setText(_translate("MainWindow", "Rear Switch", None))
        self.brake_button.setText(_translate("MainWindow", "Brake", None))

    def __speed_up(self):
        print "up"
        self.sock.sendall("1/")
        time.sleep(150/1000)

    def __speed_down(self):
        print "down"
        self.sock.sendall("2/")
        time.sleep(150/1000)

    def __brake(self):
        print "brake"
        self.sock.sendall("3/")
        time.sleep(150/1000)

    def __go_left(self):
        print "left"
        self.sock.sendall("5/")
        time.sleep(150/1000)

    def __go_right(self):
        print "right"
        self.sock.sendall("4/")
        time.sleep(150/1000)

    def __rear(self):
        print "rear"
        self.sock.sendall("6/")
        time.sleep(150/1000)

    def key_press_event(self, event):
        """
        key press
        """
        key = event.key()
        if chr(key) == 'W':
            self.__speed_up()
        if chr(key) == 'A':
            self.__go_left()
        if chr(key) == 'S':
            self.__speed_down()
        if chr(key) == 'D':
            self.__go_right()
        if chr(key) == 'M':
            self.__brake()
        if chr(key) == 'R':
            self.__rear()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Controller()
    ui.connect()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    print >>sys.stderr, 'closing socket'
    ui.sock.close()
