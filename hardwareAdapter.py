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

    def heatingON(self):
        GPIO.output(18, True)

    def heatingOFF(self):
        GPIO.output(18, False)

    def coolingON(self):
        GPIO.output(16, True)

    def coolingOFF(self):
        GPIO.output(16, False)

    def getTemparatureCooling(self):
        value = self.spi.read(0)
        cool = value/10
        return ((cool * 2.5043) / (4096 * 4.7)- 0.14993)*100

    def getTemperatureHeating(self):
        value = self.spi.read(2)
        heat = (value+.0001)/10000
        return 3.606 * (heat * heat) + 128.58 * heat - 242.86


    def display(self,value):
        a=1

if __name__ == '__main__':
    hA=hardwareAdapter()
    hA.coolingON()
    time.sleep(15)
    print "Temperatur Kuehlung: %2f",hA.getTemparatureCooling()
    hA.coolingOFF()
    time.sleep(15)
    print "Temperatur Kuehlung: %2f",hA.getTemparatureCooling()
    hA.heatingON()
    time.sleep(15)
    print "Temperatur Heizung: %2f",hA.getTemparatureHeating()
    hA.heatingOFF()
    time.sleep(15)
    print "Temperatur Heizung: %2f",hA.getTemparatureHeating()
