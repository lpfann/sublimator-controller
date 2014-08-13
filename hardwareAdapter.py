#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit
import MCP3208
import time
import Adafruit_MCP4725 as MCP4725

# Heiz- und Kuehlelemente Pins
HEAT = 18
COOL = 16
DA_ADDRESS=0x60
TARGET_LIGHT_VALUE=3685


class hardwareAdapter:
    def __init__(self):
        #Konfiguration der GPIO-Pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(HEAT, GPIO.OUT)
        GPIO.setup(COOL, GPIO.OUT)

        atexit.register(self.gpioOFF)

        # Initialisierung des A/D Wandlers,
        self.spi = MCP3208.MCP3208(0)

        # Initialisierung des D/A Wandlers
        self.da=MCP4725.MCP4725(DA_ADDRESS)
        self.start_brightness=self.configLightBarrier(debug=True)


    def gpioOFF(self):
        #Ausschalten der Pins
        GPIO.output(HEAT, False)
        GPIO.output(COOL, False)
        GPIO.cleanup()
        self.setLedVoltage(0)

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
        temperature = ((value * 2.5043) / (4096 * 4.7) - 0.14993) * 100
        return round(temperature, 2)

    def getTemperatureHeating(self):
        value = self.spi.read(2)
        heat = (value + .0001) / 1000
        temperature = 3.606 * (heat * heat) + 128.58 * heat - 242.86
        return round(temperature, 2)

    def setLedVoltage(self,voltage):
        self.da.setVoltage(voltage,persist=True)

    def configLightBarrier(self,tolerance=30,debug=False):
        brightness=self.getBrightness()
        mini=500
        maxi=3500
        voltage=(mini+maxi)/2
        i=0
        start=time.time()+0.0
        actual=start
        while(actual-start<600):
            mini=mini-200
            maxi=maxi+200
            if mini<0:
                mini=0
            if maxi > 4000:
                maxi=4000
            brightness=self.getBrightness()
            while(abs(brightness-TARGET_LIGHT_VALUE)>=tolerance):
                self.setLedVoltage(voltage)
                time.sleep(10)
                brightness=self.getBrightness()
                if debug:
                    print(i,voltage,brightness,time.time()-start)
                    i+=1
                if brightness > TARGET_LIGHT_VALUE:
                    maxi=voltage
                else:
                    mini=voltage
                voltage=(mini+maxi)/2
            if debug:
                print(i,voltage,brightness,time.time()-start)
            actual=time.time()
        return brightness+0.0

    def getBrightness(self):
        return self.spi.read(3)

    """
    Prototyp-Funktion liefert die Intensitaet der Schranke im Bereich [0,1] in Bezug zum Ausgangswert
    """
    def getIntensity(self):
        return self.spi.read(3)/self.start_brightness

if __name__ == '__main__':
    hA = hardwareAdapter()
    for i in range(50):
        print(i,hA.getIntensity())
        time.sleep(2)