# Server side code
from socket import *
import sys

# Establish default server port
serverPort = 1234

# Checking arguments to change server port
# otherwise use default
if len(sys.argv) == 2:
    serverPort = int(sys.argv[1])
print("Server port:", serverPort)

# Creating data transfer port
dataPort = serverPort + 1

# Create TCP sockets for content and data
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket2 = socket(AF_INET, SOCK_STREAM)

# Bind the socket to the port
serverSocket.bind(('', serverPort))
serverSocket2.bind(('', dataPort))

# Start listening for incoming connections
serverSocket.listen(1)
print("Ready to accept a connection..")

# Accept a connection; get client's socket
controlSocket, addr = serverSocket.accept()
print("Accepted connection from client:", addr)

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):
    # The buffer
    recvBuff = ""

    # The temporary buffer
    tmpBuff = ""

    # Keep receiving till all is received
    while len(recvBuff) < numBytes:

        # Attempt to receive bytes
        tmpBuff = sock.recv(numBytes)

        # The other side has closed the socket
        if not tmpBuff:
            break

        # Add the received bytes to the buffer
        tmpBuff = tmpBuff.decode()
        recvBuff += tmpBuff

    return recvBuff


# Accept incoming control commands until 'quit'
while 1:

    # Receive the control command
    cmd = controlSocket.recv(4096)
    cmd = cmd.decode()
    cmd = cmd.split()
    print()

    # Receive data from client and print it
    if cmd[0] == "put" and len(cmd) == 2:
        print("SUCCESS:", cmd[0], cmd[1])
        serverSocket2.listen(1)
        dataSocket, addr = serverSocket2.accept()
        fileData = ""
        recvBuff = ""
        fileSize = 0
        fileSizeBuff = ""
        fileSizeBuff = recvAll(dataSocket, 10)
        fileSize = int(fileSizeBuff)
        fileData = recvAll(dataSocket, fileSize)
        print("The file data is:")
        print(fileData)
        dataSocket.close()
    elif cmd[0] == "get":
        # NEED TO CREATE THIS
        print("IN DEVELOPMENT")
    elif cmd[0] == "ls":
        # NEED TO CREATE THIS
        print("IN DEVELOPMENT")
    elif cmd[0] == "quit":
        print("SUCCESS:", cmd[0])
        print("Server now closing..")
        break
    else:
        print("FAILURE: Invalid command")

# Close control socket upon shut down of server
controlSocket.close()