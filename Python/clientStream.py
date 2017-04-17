import cv2
import numpy
import socket
import sys
import pickle
import struct ### new code
cap=cv2.VideoCapture(0)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('192.168.0.104', 8089))
while True:
	ret,frame=cap.read()
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
	result, encimg = cv2.imencode('.jpg', frame, encode_param)
	data = numpy.array(encimg)
	stringData = data.tostring()

	clientsocket.send(str(len(stringData)).ljust(4096))
	clientsocket.send(stringData)

clientsocket.close()
