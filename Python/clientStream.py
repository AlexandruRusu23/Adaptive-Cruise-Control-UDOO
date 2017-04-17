import cv2
import numpy
import socket
import sys

def recvall(sock, count):
    """
    receive blocks of count size
    """
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('192.168.0.104', 8088))
while True:
	length = recvall(clientsocket, 4096)
	if length is None:
		break
	stringData = recvall(clientsocket, int(length))
	if stringData is None:
		break
	data = numpy.fromstring(stringData, dtype='uint8')

	frame = cv2.imdecode(data, 1)
	cv2.imshow('frameClient', frame)
	k = cv2.waitKey(33)
	if k == 27:
		break

clientsocket.close()
