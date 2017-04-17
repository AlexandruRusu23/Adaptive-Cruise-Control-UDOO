import socket
import sys
import cv2
import pickle
import numpy
import struct ## new

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

HOST='192.168.0.104'
PORT=8089

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print 'Socket created'

s.bind((HOST,PORT))
print 'Socket bind complete'
s.listen(10)
print 'Socket now listening'

conn,addr=s.accept()

while True:

    length = recvall(conn, 4096)
    stringData = recvall(conn, int(length))
    data = numpy.fromstring(stringData, dtype='uint8')

    frame=cv2.imdecode(data, 1)
    frame=cv2.flip(frame,1)
    cv2.imshow('frame', frame)
    k = cv2.waitKey(33)
    if k==27:    # Esc key to stop
        break

conn.close()
