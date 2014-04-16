#!/usr/bin/env python3

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
        spi = MCP3208.MCP3208(0)

        atexit.register(self.gpioOFF)

    def gpioOFF(self):
        #Ausschalten der Pins
        GPIO.output(18, False)
        GPIO.output(16, False)

    def heatingON(self):
        GPIO.output(18, True)

    def heatingOFF(self):
        GPIO.output(18, False)

    def coolingON(self):
        GPIO.output(16, True)

    def coolingOFF(self):
        GPIO.output(16, False)

    def getTemparature(self):
        return 0

    def display(self,value):
        a=1

if __name__ == '__main__':
    hA=hardwareAdapter()
    hA.coolingON()
    time.sleep(5)
    hA.coolingOFF()
    time.sleep(5)
    hA.heatingON()
    time.sleep(5)
    hA.heatingOFF()

