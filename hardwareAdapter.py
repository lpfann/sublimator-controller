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

    def getTemperatureCooling(self):
        value=0
        value += self.spi.read(0)
        cool = value
        print "Kuehlung Bit: %d" %(cool)
        temperature=((cool * 2.5043) / (4096 * 4.7)- 0.14993)*100
        return round(temperature,2)

    def getTemperatureHeating(self):
        value=0
        value += self.spi.read(2)
        print "Heizung Bit: %d" % (value)
        heat = (value+.0001)/1000
        temperature=3.606 * (heat * heat) + 128.58 * heat - 242.86
        return round(temperature,2)


    def display(self,value):
        a=1

if __name__ == '__main__':
    hA=hardwareAdapter()
    hA.coolingON()
    hA.heatingON()
    while True:
        print "Temperatur Kuehlung: %2f" %(hA.getTemperatureCooling())
        print "Temperatur Heizung: %2f" %(hA.getTemperatureHeating())
        time.sleep(5)