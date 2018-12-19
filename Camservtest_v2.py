import cv2
import numpy as np #Needed for opencv it seems, also used in camcap()
import socket

def initserv():
    sendsocketip = '192.168.5.3' #PC
    sendsocketport = 55555

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendsock.bind((sendsocketip, sendsocketport))

    return sendsock

def reconnector(sendsock):

    sendsock.listen()
    connection, fromadress = sendsock.accept()

    return connection


def connector():
    recsocketip = '192.168.3.10' 
    recsocketport = 33333

    print("attempting connection to client")

    recsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recsock.connect((recsocketip, recsocketport))

    return recsock


def showframe(connection):
    data = b""
    while True:
        package = connection.recv(16)
        if not package:
            package = b""
            break
        data += package

    encodedframe = data

    connection.shutdown(socket.SHUT_RDWR)
    connection.close()

    shapedframe = np.frombuffer(encodedframe, np.uint8).reshape((120,160,3))

    return shapedframe

def linecalulator(frame, oldlinex):

    width = 160
    height = 120

    Blackline = cv2.inRange(frame, (0,0,0), (70,70,70))

    img, contours, hierachy = cv2.findContours(Blackline.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        x,y,w,h = cv2.boundingRect(contours[0])

        linex = int(x+(w/2))

        cv2.line(frame, (linex,0), (linex, height), (255,0,0),3)

    else:
        print("No contour found")
        linex=oldlinex
        oldlinex = linex

    cv2.imshow("ServerframeX", frame)

    if cv2.waitKey(1) == ord('q'):  #Allows for quitting the frame
        #Was changed back to 1 as it needs it to exist in a timeframe
        #for it to display the frame and go forward in the code
        cv2.destroyAllWindows() 

    return linex, oldlinex

def PIDcont(linex, cumError, lastError):
    pval = 1
    ival = 0.1
    dval = 3
    setpoint = 80
    MaxCorr = 160
    MinCorr = -160
    
    error = setpoint - linex
    pcorr = pval * error

    # ^ P

    cumError = cumError + error
    icorr = ival*cumError

    # ^ I

    slope = error - lastError
    dcorr = slope * dval
    lastError = error

    # ^ D

    corr = pcorr + icorr + dcorr

    if corr > MaxCorr:
        corr = MaxCorr
    if corr < MinCorr:
        corr = MinCorr

    print("Correction", str(corr))

    return(corr, cumError, lastError)


def sendval(recsock, corr):

    recsock.sendall(str(corr).encode('utf-8'))
    recsock.close()


def main():
    cumError = 0
    lastError = 0
    oldlinex = 80
    sendsock = initserv()
    while True:
        connection = reconnector(sendsock) #accept connection on sendock
        nonbyteframe = showframe(connection) #gey frame over sendsock
        linex, oldlinex = linecalulator(nonbyteframe, oldlinex) 
        corr, cumError, lastError = PIDcont(linex, cumError, lastError)
        recsock = connector()
        sendval(recsock, corr)
        print(corr)

main()