#!/usr/bin/python3

from gpiozero import MCP3008
import RPi.GPIO as GPIO
from time import sleep 
import numpy as np #Needed for opencv it seems, also used in camcap()
import cv2
import socket

#import ends

host_ip = '192.168.3.1'
host_port = 44444

MCP3008(channel=0, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)

MCP0=MCP3008(0)

GPIO.setmode(GPIO.BCM)
inchan_list = 27 #Insert Anime joke here
outchan_list = [21,20,26,19,16,13,6,5] #-\\-

forward_list = [21,19,13,6] #All channels that make the wheels go forward
forward_stop = [20,26,16,5] #Reverse, but also to turn the other direction off
left_list = [26,16,21,6] #to turn car left / left motors go back
right_list = [19,13,20,5] # -\\- right
all_list = [20,19,13,5,21,26,16,6]

GPIO.setup(inchan_list, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Sets them up as inputs
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

#motorlist end

#mfl = f(19) b(26)
#mbl = f(13) b(16)
#mfr = f(21) b(20)
#mbr = f(6)  b(5)


# ^ = PID-Legacy-code

#Motorpins end

cap = cv2.VideoCapture(0)
width = 160
height = 120
ret = cap.set(3,width)
ret = cap.set(4,height)
#All this shit defines the taken picture

# ^ =cam setup, set here to make it global

pwmflf.start(0)
pwmblf.start(0)
pwmfrf.start(0)
pwmbrf.start(0)
pwmflb.start(0)
pwmblb.start(0)
pwmfrb.start(0)
pwmbrb.start(0)


def main():
    try:

        pval = 3.5
        ival = 0.01
        dval = 4
        setpoint = 80
        MaxCorr = 100
        MinCorr = -100

        desireddc = 100

        info_list = []

        sock = socketconnect(host_ip, host_port)  

        print("start")
        while True:

            print("IDLE")

            cumError = 0
            lastError = 0
            oldlinex = 80
            info_count = 0

            while not GPIO.input(27):
                pass

            while GPIO.input(27):
                pass

            sleep(0.2)

            print("ACTIVE")
            while not GPIO.input(27):
                linex, oldlinex = camcap(oldlinex)
                corr, cumError, lastError = PIDcont(linex, cumError, lastError, pval, \
                    ival, dval, setpoint, MaxCorr, MinCorr)

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


                info_count += 1
                if info_count == 30:
                    info_list.append("MCP3008: " + str(checkvalMCP0(MCP0)))
                    info_list.append("Linex :" + str(linex))
                    info_list.append("Powerleft: " + str(powerleft))
                    info_list.append("Powerright: " + str(powerright))
                    sock.sendall(str(info_list).encode('utf-8'))
                    info_count = 0
                    info_list = []

            pwmflf.ChangeDutyCycle(0)
            pwmblf.ChangeDutyCycle(0)
            pwmfrf.ChangeDutyCycle(0)
            pwmbrf.ChangeDutyCycle(0)
            pwmflb.ChangeDutyCycle(0)
            pwmblb.ChangeDutyCycle(0)
            pwmfrb.ChangeDutyCycle(0)
            pwmbrb.ChangeDutyCycle(0)

            while GPIO.input(27):
                pass

            sleep(0.2)

    except KeyboardInterrupt:
        GPIO.cleanup()

def socketconnect(host_ip, host_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host_ip, host_port))
    return sock

def PIDcont(linex, cumError, lastError, pval, ival, dval, setpoint, MaxCorr, MinCorr):

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

    return(corr, cumError, lastError)
    

def camcap(oldlinex):
    ret, frame = cap.read()
    if cap.isOpened() == 0:
        cap.open(0)

    Blackline = cv2.inRange(frame, (0,0,0), (110,110,110))

    img, contours, hierachy = cv2.findContours(Blackline.copy(), cv2.RETR_TREE, \
        cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        x,y,w,h = cv2.boundingRect(contours[0])

        linex = int(x+(w/2))


    else:
        linex=oldlinex

    return linex, oldlinex


#left_list = [26,16,21,6] #to turn car left
#right_list = [19,13,20,5] # -\\- right


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

#function end

main()

GPIO.cleanup()

#Code end
