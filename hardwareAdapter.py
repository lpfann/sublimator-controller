#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit
import MCP3208
import time
import Adafruit_MCP4725 as MCP4725
import threading

class hardwareAdapter:

    __activeLightBarrier__=False

    def __init__(self,heat=18,cool=16,daAdress=0x60,targetLightValue=3685,activateLightBarrier=False):
        # Heiz- und Kuehlelemente Pins
        self.__HEAT__=heat
        self.__COOL__=cool
        self.__DA_ADRESS__=daAdress
        self.__TARGET_LIGHT_VALUE__=targetLightValue

        #Konfiguration der GPIO-Pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.__HEAT__, GPIO.OUT)
        GPIO.setup(self.__COOL__, GPIO.OUT)

        atexit.register(self.gpioOFF)

        # Initialisierung des A/D Wandlers,
        self.spi = MCP3208.MCP3208(0)

        # Initialisierung des D/A Wandlers
        self.da=MCP4725.MCP4725(self.__DA_ADRESS__)

        self.threadSignal=threading.Event()
        if activateLightBarrier:
            self.configLightBarrier(debug=False)

    def gpioOFF(self):
        #Ausschalten der Pins
        GPIO.output(self.__HEAT__, False)
        GPIO.output(self.__COOL__, False)
        GPIO.cleanup()
        self.setLedVoltage(0)

    def start(self):
        self.heatingON()
        self.coolingON()

    def heatingON(self):
        GPIO.output(self.__HEAT__, True)

    def heatingOFF(self):
        GPIO.output(self.__HEAT__, False)

    def coolingON(self):
        GPIO.output(self.__COOL__, True)

    def coolingOFF(self):
        GPIO.output(self.__COOL__, False)

    def getTemperatureCooling(self):
        value = self.spi.read(0)
        temperature = ((value * 2.5043) / (4096 * 4.7) - 0.14993) * 100
        return round(temperature, 2)

    def getTemperatureHeating(self):
        value = self.spi.read(2)
        heat = (value + .0001) / 1000
        temperature = 3.606 * (heat * heat) + 128.58 * heat - 242.86
        return round(temperature, 2)

    def setLedVoltage(self,voltage,persist=True):
        self.da.setVoltage(voltage,persist=persist)

    def __configureLightBarrier__(self,stopSignal,tolerance=30,debug=False,waitTimeChange=10,waitTimeLoop=5,loopTime=600):
        self.__activeLightBarrier__=False
        brightness=self.getBrightness()
        mini=500
        maxi=3500
        voltage=(mini+maxi)/2
        i=0
        start=time.time()+0.0
        actual=start
        while(actual-start<loopTime):
            if stopSignal.is_set():
                self.setLedVoltage(0)
                self.__activeLightBarrier__=False
            brightness=self.getBrightness()
            if abs(brightness-self.__TARGET_LIGHT_VALUE__) >= tolerance:
                if brightness < self.__TARGET_LIGHT_VALUE__:
                    maxi=maxi+(maxi/2)
                    if maxi > 4000:
                        maxi=4000
                else:
                    mini=mini/2
            while(abs(brightness-self.__TARGET_LIGHT_VALUE__)>=tolerance):
                if stopSignal.is_set():
                    self.setLedVoltage(0)
                    self.__activeLightBarrier__=False
                self.setLedVoltage(voltage)
                time.sleep(waitTimeChange)
                brightness=self.getBrightness()
                if debug:
                    print(i,voltage,brightness,time.time()-start)
                    i+=1
                if brightness > self.__TARGET_LIGHT_VALUE__:
                    maxi=voltage
                else:
                    mini=voltage
                voltage=(mini+maxi)/2
            if debug:
                print(i,voltage,brightness,time.time()-start)
            time.sleep(waitTimeLoop)
            actual=time.time()
        self.start_brightness=brightness+0.0
        self.__activeLightBarrier__=True

    def getBrightness(self):
        return self.spi.read(3)

    def configLightBarrier(self,tolerance=30,debug=False,waitTimeChange=10,waitTimeLoop=5,runTime=600):
        try:
            if not self.activeConfugaration():
                self.threadSignal.clear()
                self.thread=threading.Thread(target=self.__configureLightBarrier__,args=(self.threadSignal,tolerance,debug,waitTimeChange,waitTimeLoop,runTime))
                self.thread.setDaemon(True)
                self.thread.start()
        except:
            print("Fehler: starten des Thread zum Konfigurieren der Lichtschranke nicht moeglich")

    def stateLightBarrier(self):
        return self.__activeLightBarrier__

    """
    Prototyp-Funktion liefert die Intensitaet der Schranke im Bereich [0,1] in Bezug zum Ausgangswert
    """
    def getIntensity(self):
        if self.stateLightBarrier():
            return self.spi.read(3)/self.start_brightness
        else:
            return -1.0

    def stopCalibrating(self):
        try:
            self.threadSignal.set()
            return True
        except:
            return False

    def activeConfugaration(self):
        try:
            return self.thread.isAlive()
        except:
            return False

if __name__ == '__main__':
    hA = hardwareAdapter()
    if hA.stateLightBarrier():
        for i in range(50):
            print(i,hA.getIntensity())
            time.sleep(2)