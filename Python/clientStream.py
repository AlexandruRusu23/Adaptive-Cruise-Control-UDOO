import cv2
import numpy as np
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
	data = pickle.dumps(frame) ### new code
	clientsocket.sendall(struct.pack("L", len(data))+data) ### new code
