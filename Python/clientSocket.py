import socket
import sys
import Controller
from PyQt4 import QtCore, QtGui

app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = Controller.Controller()
ui.setupUi(MainWindow)
MainWindow.show()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.168.0.106', 13360)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    while True:
	    # Send data
	    message = input('Your message: ')

	    if message == "close":
	    	 break
	    print >>sys.stderr, 'sending "%s"' % message
	    sock.sendall(message)
finally:
	print >>sys.stderr, 'closing socket'
	sock.close()
	sys.exit(app.exec_())
