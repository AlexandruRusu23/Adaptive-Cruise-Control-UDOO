import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('192.168.0.104', 32654)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address

        while True:
            data = connection.recv(1024)
            print >>sys.stderr, 'Client: "%s"' % data
            if data:
                input_var = input("Your answer: ")
                print >>sys.stderr, 'You sent: %s ' % input_var
                connection.sendall(input_var)
            else:
                print >>sys.stderr, 'no more data from', client_address
                break

    finally:
        # Clean up the connection
        connection.close()
