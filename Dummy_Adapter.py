import time
import thread
import random
class hardwareAdapter:
    '''
        hardwareAdapter with Dummy Data for testing purposes
    '''

    def __init__(self,heat=18,cool=16,daAdress=0x60,targetLightValue=3685,activateLightBarrier=False):
        self.coolTemp=22
        self.heatTemp=24
        self.cooling=False
        self.heating=False

        if activateLightBarrier:
            self.configLightBarrier()
        else:
            self.__activeLightBarrier__=False

    def start(self):
        self.heatingON()
        self.coolingON()

    def heatingON(self):
        self.heating=True

    def heatingOFF(self):
        self.heating=False

    def coolingON(self):
        self.cooling=True

    def coolingOFF(self):
        self.cooling=False

    def getTemperatureCooling(self):
        if self.cooling:
            self.coolTemp=self.coolTemp-random.uniform(0.5,2)
        else:
            self.coolTemp=self.coolTemp+random.uniform(0,1.5)
        return self.coolTemp

    def getTemperatureHeating(self):
        if self.heating:
            self.heatTemp=self.heatTemp+random.uniform(1,5)
        else:
            self.heatTemp=self.heatTemp-random.uniform(0.5,2)
        return self.heatTemp

    def setLedVoltage(self,voltage,persist=True):
        return


    def __configureLightBarrier__(self,tolerance=30,debug=False,waitTimeChange=10,waitTimeLoop=5,loopTime=600):
        self.__activeLightBarrier__=False
        time.sleep(loopTime)
        self.brightness=3960
        self.brightAct=self.brightness
        self.__activeLightBarrier__=True

    def getBrightness(self):
        self.brightAct=self.brightAct+random.randint(-20,20)
        if self.brightAct==0:
            self.brightAct=0
        elif self.brightActf==4095:
            self.brightAct=4095
        return self.brightAct

    def configLightBarrier(self,tolerance=30,debug=False,waitTimeChange=10,waitTimeLoop=5,loopTime=600):
        try:
            thread.start_new_thread(self.__configureLightBarrier__(),(tolerance,debug,waitTimeChange,waitTimeLoop,loopTime,))
        except:
            print("Fehler: starten des Thread zum Konfigurieren der Lichtschranke nicht moeglich")

    def stateLightBarrier(self):
        return self.__activeLightBarrier__

    def getIntensity(self):
        if self.stateLightBarrier():
            return self.getBrightness()/self.brightness
        else:
            return -1.0