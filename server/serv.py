# Server side code
from socket import *
import os, sys

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
        print("SUCCESS:", cmd[0], cmd[1])
        serverSocket2.listen(1)

        # First test to see if file exists and open it
        fileExists = False
        fileObj = ""
        try:
            fileObj = open(cmd[1], "r")
            fileExists = True
        except OSError as e:
            print(e)

        if fileExists:
            # Send the command statement to server
            controlSocket.send((cmd[0] + " " + cmd[1]).encode())
            
            # Accept connections
            dataSocket, addr = serverSocket2.accept()

            # Send the data w/ append to transfer bytes size and print
            bytesSent = 0
            fileData = None
            while 1:
                fileData = fileObj.read(65536)
                if fileData:
                    dataSizeStr = str(len(fileData))
                    while len(dataSizeStr) < 10:
                        dataSizeStr = "0" + dataSizeStr
                    fileData = dataSizeStr + fileData
                    fileData = fileData.encode()
                    while len(fileData) > bytesSent:
                        bytesSent += dataSocket.send(fileData[bytesSent:])
                else:
                    break
            print("File:", cmd[1] + "\t\t", "Bytes:", bytesSent - 10)
            dataSocket.close()

    elif cmd[0] == "ls":
        # returns all the files names inside the server directory
        print("SUCCESS:", cmd[0])
        serverSocket2.listen(1)
        dataSocket, addr = serverSocket2.accept()
        fileList = ""
        bytesSent = 0

        for file in os.listdir():
            if ".py" in file:
                continue
            else:
                fileList = fileList + file + "\n"
        dataSizeStr = str(len(fileList))
        while len(dataSizeStr) < 10:
            dataSizeStr = "0" + dataSizeStr
        fileData = dataSizeStr + fileList
        fileData = fileData.encode()
        while len(fileData) > bytesSent:
            bytesSent += dataSocket.send(fileData[bytesSent:])
        print("Files:", fileList, "Bytes:", bytesSent - 10)
        dataSocket.close()
    elif cmd[0] == "quit":
        print("SUCCESS:", cmd[0])
        print("Server now closing..")
        break
    else:
        print("FAILURE: Invalid command")

# Close control socket upon shut down of server
controlSocket.close()