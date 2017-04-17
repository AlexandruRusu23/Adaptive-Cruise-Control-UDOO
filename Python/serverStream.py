import socket
import sys
import time
import cv2
import numpy
HOST='192.168.0.104'
PORT=8088

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print 'Socket created'

sock.bind((HOST,PORT))
print 'Socket bind complete'
sock.listen(1)
print 'Socket now listening'

while True:

    print >>sys.stderr, 'waiting for a connection'
    conn,addr=sock.accept()

    try:
        print >>sys.stderr, 'connection from', addr
        cap=cv2.VideoCapture(0)

        current_time = time.time()

        while True:
            ret,frame=cap.read()
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            result, encimg = cv2.imencode('.jpg', frame, encode_param)
            data = numpy.array(encimg)
            stringData = data.tostring()

            if time.time() - current_time > 10:
                break

            conn.send(str(len(stringData)).ljust(4096))
            conn.send(stringData)

    finally:
        conn.close()
        cap.release()
