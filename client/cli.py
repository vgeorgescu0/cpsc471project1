# Client side code
from socket import *
import sys

# Establish default server name and port
serverName = "localhost"
serverPort = 1234

# Checking arguments to change server name and port
# otherwise use default
if len(sys.argv) == 3:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
print("Server name:", serverName, "Server port:", serverPort)

# Creating data transfer port
dataPort = serverPort + 1

# Connect to control socket
controlSocket = socket(AF_INET, SOCK_STREAM)
controlSocket.connect((serverName, serverPort))

# Show a list of client commands
print("Command list: put <filename>; get <filename>; ls; quit")

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


while 1:
    # Receive input command from client
    cmd = input("ftp> ")
    cmd = cmd.split()

    # Process input
    if cmd[0] == "put" and len(cmd) == 2:

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

            # Create a data socket and connect to the data port
            dataSocket = socket(AF_INET, SOCK_STREAM)
            dataSocket.connect((serverName, dataPort))

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
    elif cmd[0] == "get":
        controlSocket.send((cmd[0] + " " + cmd[1]).encode())

        dataSocket = socket(AF_INET, SOCK_STREAM)
        dataSocket.connect((serverName, dataPort))

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
    elif cmd[0] == "ls":
        # Send conmmand to server to list all files on server
        controlSocket.send(cmd[0].encode())

        dataSocket = socket(AF_INET, SOCK_STREAM)
        dataSocket.connect((serverName, dataPort))

        fileData = ""
        recvBuff = ""
        fileSize = 0
        fileSizeBuff = ""
        fileSizeBuff = recvAll(dataSocket, 10)
        fileSize = int(fileSizeBuff)
        fileData = recvAll(dataSocket, fileSize)
        print("Files in the server directory:")
        print(fileData)
        dataSocket.close()
    elif cmd[0] == "quit":
        # Send the command statement to server then end script
        controlSocket.send(cmd[0].encode())
        break
    else:
        print("Invalid command, try again..")

# Close the socket
controlSocket.close()
