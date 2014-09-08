import time
import threading
import random

class Dummy_Adapter:
    '''
        hardwareAdapter with Dummy Data for testing purposes
    '''
    def __init__(self,heat=18,cool=16,daAdress=0x60,targetLightValue=3685,activateLightBarrier=False):
        self.coolTemp=22
        self.heatTemp=24
        self.cooling=False
        self.heating=False

        self.threadSignal=threading.Event()

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


    def __configureLightBarrier__(self,stopSignal,tolerance=30,debug=False,waitTimeChange=10,waitTimeLoop=5,loopTime=600):
        self.__activeLightBarrier__=False
        start=time.time()+0.0
        actual=start
        if debug:
            i=1
        while(actual-start<loopTime):
            if debug:
                print(i,stopSignal.is_set())
            if stopSignal.is_set():
                if debug:
                    print(i,"Stopp")
                exit()
            time.sleep(waitTimeLoop)
            actual=time.time()
            i=i+1
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

    def configLightBarrier(self,tolerance=30,debug=False,waitTimeChange=10,waitTimeLoop=5,runTime=600):
        try:
            if not self.activeConfiguration():
                self.threadSignal.clear()
                self.thread=threading.Thread(target=self.__configureLightBarrier__,args=(self.threadSignal,tolerance,debug,waitTimeChange,waitTimeLoop,runTime))
                self.thread.start()
        except:
            print("Fehler: starten des Thread zum Konfigurieren der Lichtschranke nicht moeglich")

    def stopCalibrating(self):
        try:
            if ha.activeConfiguration():
                self.threadSignal.set()
                return True
            else:
                return False
        except:
            return False

    def stateLightBarrier(self):
        return self.__activeLightBarrier__

    def activeConfiguration(self):
        try:
            return self.thread.isAlive()
        except:
            return False

    def getIntensity(self):
        if self.stateLightBarrier():
            return self.getBrightness()/self.brightness
        else:
            return -1.0

if __name__=='__main__':
    ha=Dummy_Adapter()
    ha.configLightBarrier(runTime=10000,debug=True)
    if ha.activeConfiguration():
        time.sleep(5)
    print(ha.stopCalibrating())