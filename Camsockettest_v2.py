import RPi.GPIO as GPIO
import cv2
import numpy as np #Needed for opencv it seems, also used in camcap()
import socket
from time import sleep

cap = cv2.VideoCapture(0)
width = 160
height = 120
ret = cap.set(3,width)
ret = cap.set(4,height)

GPIO.setmode(GPIO.BCM)
#inchan_list = [27,23,22] #Insert Anime joke here
outchan_list = [21,20,26,19,16,13,6,5] #-\\-

forward_list = [21,19,13,6] #All channels that make the wheels go forward
forward_stop = [20,26,16,5] #Reverse, but also to turn the other direction off
left_list = [26,16,21,6] #to turn car left / left motors go back
right_list = [19,13,20,5] # -\\- right
all_list = [20,19,13,5,21,26,16,6]

#GPIO.setup(inchan_list, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Sets them up as inputs
GPIO.setup(outchan_list, GPIO.OUT, initial=GPIO.LOW) #Sets them up as outputs


freq= 15

#setup end


pwmflf = GPIO.PWM(19,freq)
pwmblf = GPIO.PWM(13,freq)
pwmfrf = GPIO.PWM(21,freq)
pwmbrf = GPIO.PWM(6, freq)
pwmflb = GPIO.PWM(26,freq)
pwmblb = GPIO.PWM(16,freq)
pwmfrb = GPIO.PWM(20,freq)
pwmbrb = GPIO.PWM(5, freq)

def motorint():
    pwmflf.start(0)
    pwmblf.start(0)
    pwmfrf.start(0)
    pwmbrf.start(0)
    pwmflb.start(0)
    pwmblb.start(0)
    pwmfrb.start(0)
    pwmbrb.start(0)

def connector():
    sendsocketip = '192.168.43.29' 
    sendsocketport = 55555

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendsock.connect((sendsocketip, sendsocketport))

    return sendsock


def serverint():
    recsocketip = '192.168.43.113'
    recsocketport = 33333

    recsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recsock.bind((recsocketip, recsocketport))

    return recsock


def serverconnector(recsock):
    print("listening")
    recsock.listen()
    connection, fromaddress = recsock.accept()

    return connection

def camcap(sendsock):
    ret, frame = cap.read(0)
    if cap.isOpened() == 0:
        cap.open(0)

    print(frame.shape)

    # cv2.imshow("FirstframeX", frame)


    # if cv2.waitKey(1) == ord('q'):  #Allows for quitting the frame
    #     #Was changed back to 1 as it needs it to exist in a timeframe
    #     #for it to display the frame and go forward in the code
    #     cap.release()
    #     cv2.destroyAllWindows()

    encodedframe = frame.tostring()

    sendsock.sendall(encodedframe)

    sendsock.shutdown(socket.SHUT_RDWR)
    sendsock.close()

    # nonbyteframe = np.frombuffer(encodedframe, np.uint8)

    # shapedframe = nonbyteframe.reshape(120,160,3) 


def recval(connection):
    data = b""
    while True:
        package = connection.recv(16)
        if not package:
            package = b""
            break
        data += package

    connection.shutdown(socket.SHUT_RDWR)
    connection.close()

    value = data.decode('utf-8')

    print("Decoded value: ", value)

    value = float(value)

    value = int(value)

    return value

def motorstate(corr):
    if corr >= -50 and corr <= 50: #forward
        allforward(100)
    elif corr > 30: #right
        power = int((corr/160)*100)
        print(power)
        turnleft(power)
    elif corr < -30: #Left
        power = int((corr/-160)*100)
        print(power)
        turnright(power)


def allforward(dc):
    pwmflf.ChangeDutyCycle(dc)
    pwmblf.ChangeDutyCycle(dc)
    pwmfrf.ChangeDutyCycle(dc)
    pwmbrf.ChangeDutyCycle(dc)
    pwmflb.ChangeDutyCycle(0)
    pwmblb.ChangeDutyCycle(0)
    pwmfrb.ChangeDutyCycle(0)
    pwmbrb.ChangeDutyCycle(0)

def backward(dc):
    pwmflf.ChangeDutyCycle(0)
    pwmblf.ChangeDutyCycle(0)
    pwmfrf.ChangeDutyCycle(0)
    pwmbrf.ChangeDutyCycle(0)
    pwmflb.ChangeDutyCycle(dc)
    pwmblb.ChangeDutyCycle(dc)
    pwmfrb.ChangeDutyCycle(dc)
    pwmbrb.ChangeDutyCycle(dc)

    
def turnleft(dc):
    pwmflb.ChangeDutyCycle(dc)
    pwmblb.ChangeDutyCycle(dc)
    pwmfrf.ChangeDutyCycle(dc)
    pwmbrf.ChangeDutyCycle(dc)
    pwmfrb.ChangeDutyCycle(0)
    pwmbrb.ChangeDutyCycle(0)
    pwmflf.ChangeDutyCycle(0)
    pwmblf.ChangeDutyCycle(0)


def turnright(dc):
    pwmflb.ChangeDutyCycle(0)
    pwmblb.ChangeDutyCycle(0)
    pwmfrf.ChangeDutyCycle(0)
    pwmbrf.ChangeDutyCycle(0)
    pwmfrb.ChangeDutyCycle(dc)
    pwmbrb.ChangeDutyCycle(dc)
    pwmflf.ChangeDutyCycle(dc)
    pwmblf.ChangeDutyCycle(dc)


def main():
    motorint()
    recsock = serverint() #starts server
    while True:
        sendsock = connector() #connect to server
        camcap(sendsock) #take and send frame over sendsock
        print("camcap sendt")
        connection = serverconnector(recsock) #connect to recsock
        value = recval(connection) #get value from recsock
        motorstate(value) 


main()

GPIO.cleanup()