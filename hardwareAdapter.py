#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit
import MCP3208
import time

class hardwareAdapter:

    def __init__(self):
        #Konfiguration der GPIO-Pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)

        # Initialisierung des A/D Wandlers,
        self.spi = MCP3208.MCP3208(0)

        atexit.register(self.gpioOFF)

    def gpioOFF(self):
        #Ausschalten der Pins
        GPIO.output(18, False)
        GPIO.output(16, False)

    def start(self):
        self.heatingON()
        self.coolingON()

    def heatingON(self):
        GPIO.output(18, True)

    def heatingOFF(self):
        GPIO.output(18, False)

    def coolingON(self):
        GPIO.output(16, True)

    def coolingOFF(self):
        GPIO.output(16, False)

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
    hA.heatingON()
    tempH=0
    tempC=0
    while True:
        tempH=hA.getTemperatureHeating()
        tempC=hA.getTemperatureCooling()
        if tempH > 161:
            hA.heatingOFF()
        elif tempH < 160:
            hA.heatingON()
        print "Temperatur(H/C): %2f  C  %2f  C" %(tempH,tempC)
        time.sleep(5)
