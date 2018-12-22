#!/usr/bin/python3

# from gpiozero import MCP3008
import RPi.GPIO as GPIO
from time import sleep 
import numpy as np #Needed for opencv it seems, also used in camcap()
import cv2

#import ends

# MCP3008(channel=0, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)

# MCP0=MCP3008(0)

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
        cumError = 0
        lastError = 0
        oldlinex = 80
        cumin = 0
        cumax = 0
        power = 0
##        allforward(50)
        #ALL below needs tuning on the numbers as the framesize was changed
        while True:
            #setpoint = 80
            linex, oldlinex = camcap(oldlinex)
            corr, cumError, lastError = PIDcont(linex, cumError, lastError)

            # Make PID for each side seperatly? 
            # Speed of left side = Desired speed - Corr
            # Speed of right side = Desired speed + Corr
            # If desired speed == 50%
            # That would give 50% to tune in
            # Base turning on differential speed-steering

            powerleft = 100 - corr
            powerright = 100 + corr

            if powerleft >= 100:
                powerleft = 100

            if powerright >= 100:
                powerright = 100

            print(powerleft)
            print(powerright)

            powleft(powerleft)
            powright(powerright)

            # if corr >= -60 and corr <= 60: #forward
            #     allforward(40)
            # elif corr > 40: #right
            #     power = int((corr/160)*100)
            #     print(power)
            #     turnleft(power)
            # elif corr < -40: #Left
            #     power = int((corr/-160)*100)
            #     print(power)
            #     turnright(power)
            #testfunc()
        #MCPvalue = checkvalMCP0(MCP0)
            print("\n")
    except KeyboardInterrupt:
        print(power)
        GPIO.cleanup()

def PIDcont(linex, cumError, lastError):
    pval = 3
    ival = 0.1
    dval = 2.4
    setpoint = 80
    MaxCorr = 200
    MinCorr = -200
    
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
    

def camcap(oldlinex):
    ret, frame = cap.read()
    if cap.isOpened() == 0:
        cap.open(0)

    Blackline = cv2.inRange(frame, (0,0,0), (120,120,120))

    img, contours, hierachy = cv2.findContours(Blackline.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # kernel = np.ones((3,3), np.uint8)

    # Blackline= cv2.erode(Blackline, kernel, iterations = 3)

    # Blackline= cv2.dilate(Blackline, kernel, iterations = 9)

    if len(contours) > 0:
        x,y,w,h = cv2.boundingRect(contours[0])

        linex = int(x+(w/2))

        cv2.line(frame, (linex,0), (linex, height), (255,0,0),3)

    else:
        linex=oldlinex

    print(linex)
    
    cv2.imshow('frame',frame)  #Shows picture in frame called "frame"

    if cv2.waitKey(1) == ord('q'):  #Allows for quitting the frame
        #Was changed back to 1 as it needs it to exist in a timeframe
        #for it to display the frame and go forward in the code
        cap.release()
        cv2.destroyAllWindows()

    return linex, oldlinex


def powleft(dc):
    if dc >= 0:
        pwmflb.ChangeDutyCycle(0)
        pwmblb.ChangeDutyCycle(0)
        pwmflf.ChangeDutyCycle(dc)
        pwmblf.ChangeDutyCycle(dc)
    else:
        dc = dc*(-1)
        pwmflb.ChangeDutyCycle(dc)
        pwmblb.ChangeDutyCycle(dc)
        pwmflf.ChangeDutyCycle(0)
        pwmblf.ChangeDutyCycle(0)


def powright(dc):
    if dc >= 0:
        pwmfrb.ChangeDutyCycle(0)
        pwmbrb.ChangeDutyCycle(0)
        pwmfrf.ChangeDutyCycle(dc)
        pwmbrf.ChangeDutyCycle(dc)
    else:
        dc = dc*(-1)
        pwmfrb.ChangeDutyCycle(dc)
        pwmbrb.ChangeDutyCycle(dc)
        pwmfrf.ChangeDutyCycle(0)
        pwmbrf.ChangeDutyCycle(0)       


# def checkvalMCP0(MCP0):
#     value = MCP0.value
#     print(value)
#     value = int(value*10)
#     return value



#left_list = [26,16,21,6] #to turn car left
#right_list = [19,13,20,5] # -\\- right

#mfl = f(19) b(26)
#mbl = f(13) b(16)
#mfr = f(21) b(20)
#mbr = f(6)  b(5)

##motordict= {  #Legacy
##    "mflf":19,
##    "mflb":26,
##    "mblf":13,
##    "mblb":16,
##    "mfrf":21,
##    "mfrb":20,
##    "mbrf":6,
##    "mbrb":5,
##    }


def testfunc(): #Legacy
    print("Test")
    GPIO.output(all_list, 0)
##    iner = input("Please enter motor\n")
##    GPIO.output(motordict[iner],1)
##    input()
##    GPIO.output(motordict[iner],1)
##    input()
    input()
    GPIO.output(right_list,1)
    input()
    GPIO.output(right_list,0)

#function end


#Event end

print("start") #Kinda not needed, looks good though

main()

GPIO.cleanup()

#Code end
