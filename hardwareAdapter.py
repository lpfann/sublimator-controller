#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit
import MCP3208
import time

#Display Steuerpins(unsicher/ungetestet)
DOG_SI=21
DOG_CLK=23
DOG_A0=24
DOG_CSB=26
DOG_RS=19

#Heiz- und Kuehlelemente Pins
HEAT=18
COOL=16

class hardwareAdapter:

    def __init__(self):
        #Konfiguration der GPIO-Pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(HEAT, GPIO.OUT)
        GPIO.setup(COOL, GPIO.OUT)
        GPIO.setup(DOG_A0,GPIO.OUT)
        GPIO.setup(DOG_CLK,GPIO.OUT)
        GPIO.setup(DOG_CSB,GPIO.OUT)
        GPIO.setup(DOG_RS,GPIO.OUT)
        GPIO.setup(DOG_SI,GPIO.OUT)

        # Initialisierung des A/D Wandlers,
        self.spi = MCP3208.MCP3208(0)

        atexit.register(self.gpioOFF)

    def gpioOFF(self):
        #Ausschalten der Pins
        GPIO.output(HEAT, False)
        GPIO.output(COOL, False)
        GPIO.cleanup()

    def initLcd(self):
        GPIO.output(DOG_RS, 0)
        time.sleep(0.01)
        GPIO.output(DOG_RS, 1)
        time.sleep(0.01)
        init_seq = [ 0x40, 0xA1, 0xC0, 0xA6, 0xA2, 0x2F, 0xF8, 0x00, 0x27, 0x81, 0x16, 0xAC, 0x00, 0xAF ]
        self.sendCmdSeq(init_seq)

    def setPos(self,page,column):
        self.sendCmd(0xB0 + page)
        self.sendCmd(0x10 + ((column&0xF0)>>4))
        self.sendCmd(0x00 + (column&0x0F))

    def clearLcd(self):
        for i in range(8):
            self.setPos(i, 0)
            self.sendDataSeq([0x00]*128)

    def sendByte(self,data):
        if type(data)==type('a'):
            data=ord(data)
        GPIO.output(DOG_CSB,0)
        for i in range(8):
            if data&128 > 0:
                GPIO.output(DOG_SI, 1)
            else:
                GPIO.output(DOG_SI, 0)
            data = data<<1
            GPIO.output(DOG_CLK, 0)
            time.sleep(0.00001)
            GPIO.output(DOG_CLK, 1)
            time.sleep(0.00001)
        GPIO.output(DOG_CSB, 1)
        time.sleep(0.01)

    def sendCmd(self,cmd):
        GPIO.output(DOG_A0, 0)
        self.sendByte(cmd)
        time.sleep(0.001)

    def sendCmdSeq(self,cmdSeq):
        for cmd in cmdSeq:
            self.sendCmd(cmd)

    def sendData(self,data):
        GPIO.output(DOG_A0,1)
        self.sendByte(data)

    def sendDataSeq(self,dataSeq):
        for data in dataSeq:
            self.sendData(data)

    def start(self):
        self.heatingON()
        self.coolingON()

    def heatingON(self):
        GPIO.output(HEAT, True)

    def heatingOFF(self):
        GPIO.output(HEAT, False)

    def coolingON(self):
        GPIO.output(COOL, True)

    def coolingOFF(self):
        GPIO.output(COOL, False)

    def getTemperatureCooling(self):
        value = self.spi.read(0)
        temperature=((value * 2.5043) / (4096 * 4.7)- 0.14993)*100
        return round(temperature,2)

    def getTemperatureHeating(self):
        value = self.spi.read(2)
        heat = (value+.0001)/1000
        temperature=3.606 * (heat * heat) + 128.58 * heat - 242.86
        return round(temperature,2)


    def display(self,value):
        a=1

if __name__ == '__main__':
    hA=hardwareAdapter()
    hA.initLcd()
    time.sleep(5)
    for i in range(8):
        data = 1
        for j in range(4):
            hA.setPos(i, 0)
            hA.sendDataSeq([data]*128)
            data += pow(4, j+1)
    for i in range(64):
        for j in range(8):
            hA.setPos(j, i*2)
            hA.sendDataSeq([ 0xFF, 0x00 ])
    hA.clearLcd()
    print "Finished"
