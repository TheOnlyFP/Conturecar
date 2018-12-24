#!/usr/bin/python3

from gpiozero import MCP3008
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


MCP3008(channel=0, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)

MCP0=MCP3008(0)


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
    sendsocketip = '192.168.3.14' #PC
    sendsocketport = 55555

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendsock.connect((sendsocketip, sendsocketport))

    return sendsock

def serverint():
    recsocketip = '192.168.5.2' #Pi
    recsocketport = 33333

    recsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recsock.bind((recsocketip, recsocketport))

    return recsock

def dataconnect():
    host_ip = '192.168.3.1'
    host_port = 44445

    datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    datasock.connect((host_ip, host_port))

    return datasock



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

    encodedframe = frame.tostring()

    sendsock.sendall(encodedframe)

    sendsock.shutdown(socket.SHUT_RDWR)
    sendsock.close()


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

def motorstate(corr, desireddc):
    powerleft = desireddc - corr
    powerright = desireddc + corr

    if powerleft >= 100:
        powerleft = 100
    elif powerleft < 0:
        powerleft = 0

    if powerright >= 100:
        powerright = 100
    elif powerright < 0:
        powerright = 0

    powleft(powerleft)
    powright(powerright)

    return powerleft, powerright


def powleft(dc):
    if dc < 0:
        dc = 0
    pwmflb.ChangeDutyCycle(0)
    pwmblb.ChangeDutyCycle(0)
    pwmflf.ChangeDutyCycle(dc)
    pwmblf.ChangeDutyCycle(dc)


def powright(dc):
    if dc < 0:
        dc = 0
    pwmfrb.ChangeDutyCycle(0)
    pwmbrb.ChangeDutyCycle(0)
    pwmfrf.ChangeDutyCycle(dc)
    pwmbrf.ChangeDutyCycle(dc)   


def checkvalMCP0(MCP0):
    value = MCP0.value
    value = (value*10)
    return value


def datasocksend(sock, powerleft, powerright, linex):
    info_list = []
    info_list.append("MCP3008: " + str(checkvalMCP0(MCP0)))
    info_list.append("Linex :" + str(linex))
    info_list.append("Powerleft: " + str(powerleft))
    info_list.append("Powerright: " + str(powerright))
    sock.sendall(str(info_list).encode('utf-8'))


def main():
    motorint()
    recsock = serverint() #starts server
    datasock = dataconnect()
    desireddc = 100
    while True:
        sendsock = connector() #connect to server
        camcap(sendsock) #take and send frame over sendsock
        print("camcap sendt")
        connection = serverconnector(recsock) #connect to recsock
        linex = recval(connection) #get value from recsock
        powerleft, powerright = motorstate(linex, desireddc) 
        datasocksend(datasock, powerleft, powerright, linex)



main()

GPIO.cleanup()