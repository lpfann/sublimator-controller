#!/usr/bin/env python2
# coding=utf-8
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Jens Schulz, Dominik Gründing, Lukas Pfannnschmidt

import os
import time
from threading import Timer
from threading import Thread
import logging
import SequenceHandler
import datetime
import StringIO

'''
    Import of hardwareAdapter if RaspberryPi Library is present.

'''
import imp
try:
    imp.find_module('RPi')
    import hardwareAdapter
    importedHardware = hardwareAdapter.hardwareAdapter() 
    print("RaspberryPi detected")
except ImportError:
    import Dummy_Adapter as hardwareAdapter
    importedHardware = hardwareAdapter.Dummy_Adapter() 
    print("No RaspberryPi detected. Using Dummy Data")


class Sublimator():

    def __init__(self):
        self.currSeq = None
        self.running = False
        self.datalog = []
        self.initLogger()
        # Hardware Adapter initalisieren
        self.hardware = importedHardware
        self.progindex = 0
        # Import der zur Verfuegung stehenden Sequenzen
        self.sequences = SequenceHandler.importSequences(self.logger)

    def initLogger(self):
        """
            Initalisiert den logger der überall, auch in den Untermodulen,
            benutzt werden kann.
            Formatierung und verschiedene Handler für Consolen und Datei Logging werden hier konfiguriert
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        filehandler = logging.FileHandler('main.log')
        filehandler.setLevel(logging.INFO)
        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        guiconsoleformatter = logging.Formatter(fmt=u'%(asctime)s - %(message)s', datefmt="%H:%M:%S")
        filehandler.setFormatter(formatter)
        consolehandler.setFormatter(formatter)
        self.log_capture_string = StringIO.StringIO()
        ch = logging.StreamHandler(self.log_capture_string)
        ch.setLevel(logging.INFO)
        ch.setFormatter(guiconsoleformatter)
        self.logger.addHandler(ch)
        self.logger.addHandler(filehandler)
        self.logger.addHandler(consolehandler)

    def counter(self):
        """
             Zeitzähler für die Programmzeiten

        """

        # Methode die im Timer Thread aufgerufen wird
        self.progindex += 1

    def tempregulator(self, targetheatingtemp, targetcoolingtemp):
        """
        Funktion, welche die Temperatur reguliert um den Zielwerten zu entsprechen
        :param targetheatingtemp: Zielwert für Heizung
        :param targetcoolingtemp: Zielwert für Kühlung
        """
        temp_delay = 2  # Temperatur-Delay um weiteres aufheizen über TargetHeatingTemp zu verhindern
        if self.hardware.getTemperatureHeating() <= targetheatingtemp - temp_delay:
            self.hardware.heatingON()
        else:
            self.hardware.heatingOFF()
        if self.hardware.getTemperatureCooling() >= targetcoolingtemp:
            self.hardware.coolingON()
        else:
            self.hardware.coolingOFF()

    def calib_start(self):
        self.hardware.configLightBarrier()

    def calib_stop(self):
        self.hardware.stopCalibrating()

    def controller(self, currSeq):
        """
            Steuert den Ablauf der Sequenz.
            Ruft mehrmals Timer auf, die entsprechend den Programmpunkten  lange laufen
        :param currSeq:
        """
        # Initalisierungen für den ersten programmpunkt
        self.progindex = 0
        self.currSeq = currSeq
        prog = self.currSeq.programs[self.progindex]
        targetheatingtemp = prog.targetHeatingTemp
        targetcoolingtemp = prog.targetCoolingTemp
        timer = Timer(prog.time, self.counter)
        timer.start()
        oldindex = self.progindex
        self.running = True
        self.datalog = []
        # Schleife die solange läuft, bis die Sequenz komplett durchlaufen ist oder von außen abgebrochen wird.
        while self.running:
            # Ablauf der Sequenz steuern
            if self.progindex < len(self.currSeq.programs) and oldindex != self.progindex:
                oldindex = self.progindex
                prog = self.currSeq.programs[self.progindex]
                timer = Timer(prog.time, self.counter)
                timer.start()
                targetheatingtemp = prog.targetHeatingTemp
                targetcoolingtemp = prog.targetCoolingTemp
            #Abbruchbedingung - Ende der Sequenz erreicht
            if self.progindex == len(currSeq.programs):
                self.running = False

            # Temperatur regulieren
            self.tempregulator(targetheatingtemp, targetcoolingtemp)
            # Ausgabe der momentanen Daten
            self.datalog.append((targetheatingtemp, self.hardware.getTemperatureHeating(),
                targetcoolingtemp, self.hardware.getTemperatureCooling(),
                str(self.hardware.getIntensity())))
            # Pause
            time.sleep(0.3)

        # Heizung und Kühlung ausschalten nach Programm
        self.hardware.heatingOFF()
        self.hardware.coolingOFF()
        self.writedatatofile(self.datalog)  # Datenlog schreiben
        self.logger.info(u"Sequence complete")

    def writedatatofile(self, datalog):
        """
            Schreibt Datenlog in eine .csv Datei um damit weiter arbeiten zu können.
        :param datalog: Der zu schreibende Datenlog
        :param currSeq: Gewählte Sequenz, mit der das Programm abgelaufen ist
        """
        if not os.path.exists("./logs"):
            os.makedirs("./logs")
        filename = "./logs/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "_" + self.currSeq.name + ".csv"
        datafile = open(filename, 'w')
        # writing header line
        datafile.write("#TargetHeating, CurrentHeating, TargetCooling, CurrentCooling, LightIntensity\n")
        for x in datalog:
            # writing each tuple from the datalog into comma seperated lines
            datafile.write(("{}, {}, {}, {}, {}\n".format(x[0], x[1], x[2], x[3], x[4] )))
        datafile.close()
        self.logger.info("Logfile with Data was created: {}".format(filename))

    def start(self, sequence):
        """
            Funktion zum Starten des Controller Threads.
            Sollte vom Starten-Button aufgerufen werden.

        :param sequence: Sequenz die vom Controller abgelaufen wird.
        """
        self.logger.info("Sequence started.")
        t = Thread(target=self.controller, args=(sequence,))
        t.start()
        # t.join()

    def stop(self):
        """
            Funktion zum stoppen des Controller Threads.
            Sollte von einem mögliche Stop-Button aufgerufen werden

        """
        self.running = False
        self.logger.info("Sequence stopped.")


if __name__ == '__main__':
    sub = Sublimator()
    currentSequence = sub.sequences[0]
    sub.start(currentSequence)
