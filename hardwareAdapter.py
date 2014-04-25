#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit
import MCP3208
import time

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

        # Initialisierung des A/D Wandlers,
        self.spi = MCP3208.MCP3208(0)

        atexit.register(self.gpioOFF)

    def gpioOFF(self):
        #Ausschalten der Pins
        GPIO.output(HEAT, False)
        GPIO.output(COOL, False)
        GPIO.cleanup()

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
        print value
        temperature=((value * 2.5043) / (4096 * 4.7)- 0.14993)*100
        return round(temperature,2)

    def getTemperatureHeating(self):
        value = self.spi.read(2)
        print value
        heat = (value+.0001)/1000
        temperature=3.606 * (heat * heat) + 128.58 * heat - 242.86
        return round(temperature,2)

if __name__ == '__main__':
    hA=hardwareAdapter()
    hA.start()
    temp=0
    cool=0
    while True:
        temp=hA.getTemperatureHeating()
        cool=hA.getTemperatureCooling()
        print "Temperatur: %2f  Kuehlung: %2f\n" %(temp,cool)
        if temp>160:
            hA.heatingOFF()
        elif temp<155:
            hA.heatingON()
        if cool<6:
            hA.coolingOFF()
        elif cool > 9:
            hA.coolingON()
        time.sleep(3)