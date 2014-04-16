#!/usr/bin/env python3

import RPi.GPIO as GPIO
import atexit
import MCP3208

class hardwareAdapter:

    def __init__(self):
        #Konfiguration der GPIO-Pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(16, True)
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, True)

        # Initialisierung des A/D Wandlers,
        spi = MCP3208.MCP3208(0)

    def __del__(self):
        #Ausschalten der Pins
        GPIO.output(18, False)
        GPIO.output(16, False)

    def heatingON(self):
        a=1

    def heatingOFF(self):
        a=1

    def getTemparature(self):
        return 0

    def display(self,value):
        a=1
