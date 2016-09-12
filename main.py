#This program implements a simple network protocol
import sys
import socket
import ssl

HEADER = 'cs3700fall2016 '
DEFAULT_PORT = 27993

#Parses the command line parameters
def getParameters():
    if (len(sys.argv) < 2):
        print 'python main.py <-p port> <-s> [hostname] [NEU ID]'
        sys.exit(1)

    ssl = False
    port = DEFAULT_PORT
    i = 0
    while ( i < len(sys.argv) - 2 ):
        if (sys.argv[i] == '-s'):
            ssl = True
        elif (sys.argv[i] == '-p'):
            port = int(sys.argv[i + 1])
            i += 1 
        i += 1

    neuId = sys.argv[-1]
    host = socket.gethostbyname(sys.argv[-2])
    return host, port, neuId, ssl


#Takes a socket and neuId, sends the initial HELLO message to the server and
#returns the response
#socket, str -> str
def sendHello(mySocket, neuId):
    msg = HEADER + 'HELLO ' + neuId + "\n"
    mySocket.send(msg)
    return mySocket.recv(256)

#Takes a socket and a solution (int), sends a SOLUTION message to the server, and 
#returns the response
#socket, str -> str
def sendSolution(mySocket, solution):
    msg = HEADER + str(solution) + "\n"
    mySocket.send(msg)
    return mySocket.recv(256)

#Handles a STATUS message from the server. Returns the solution as a string
#str -> str
def handleStatus(message):
    tokens = message.split()
    try:
        n0 = int(tokens[2].rstrip())
        operator = tokens[3].rstrip()
        n1 = int(tokens[4].rstrip())
    
        if operator == '+':
            return str(n0 + n1)
        elif operator == '-':
            return str(n0 - n1)
        elif operator == '*':
            return str(n0 * n1)
        elif operator == '/':
            return str(n0 / n1)
    except:
        print "***WARNING*** bad status message: " + message
        sys.exit(0)

#Handles a BYE message and returns the secret key
#str -> str
def handleBye(message):
    tokens = message.split()
    try:
        return tokens[-1]
    except:
        print "***WARNING*** bad BYE message: " + message
        sys.exit(0)


#Interprets a response from the server, returns true if the connection should stay open
#str -> bool
def interpretMessage(message):
    tokens  = message.split()
    if tokens[1] == 'STATUS':
       return True, handleStatus(message)
    elif tokens[1] == 'BYE':
       return False, handleBye(message)
    else:
        print "***WARNING*** unkown message from server: " + message
        sys.exit(1)
 
#Main function
def main():
   
    #Establish connection to server
    host, port, neuId, ssl = getParameters()
    print 'connecting to ' + host + '...'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if ssl:
        s = ssl.wrap_socket(s)       
    s.connect((host, port))
    print 'connection established'
    
    connectionOpen, message = interpretMessage(sendHello(s, neuId))
    while connectionOpen:
        connectionOpen, message = interpretMessage(sendSolution(s, message))
    
    print 'Secret Key: ' + message
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    print 'connection closed'

if __name__ == '__main__':
    main()
