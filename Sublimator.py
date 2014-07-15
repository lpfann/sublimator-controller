#!/usr/bin/env python2
# coding=utf-8
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries
import os
import random
import time
from threading import Timer
from threading import Thread
import logging
import SequenceHandler
# import hardwareAdapter
import datetime
import StringIO
#import matplotlib.pyplot as plt



class Sublimator():
    def __init__(self):
        self.currSeq = None
        self.running = False
        self.datalog = []
        self.initLogger()
        # Hardware Adapter initalisieren
        # self.hardware = hardwareAdapter.hardwareAdapter()
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
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        filehandler.setFormatter(formatter)
        consolehandler.setFormatter(formatter)
        self.log_capture_string = StringIO.StringIO()
        ch = logging.StreamHandler(self.log_capture_string)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
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
        # if self.hardware.getTemperatureHeating() <= targetheatingtemp - temp_delay:
        # self.hardware.heatingON()
        # else:
        #     self.hardware.heatingOFF()
        # if self.hardware.getTemperatureCooling() >= targetcoolingtemp:
        #     self.hardware.coolingON()
        # else:
        #     self.hardware.coolingOFF()


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
        # plt = initlog()
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
            # datalog.append((targetheatingtemp, self.hardware.getTemperatureHeating(),targetcoolingtemp, self.hardware.getTemperatureCooling()))
            self.datalog.append((targetheatingtemp, 0, targetcoolingtemp, 0))
            # Pause
            time.sleep(0.3)

        # Heizung und Kühlung ausschalten nach Programm
        # self.hardware.heatingOFF()
        # self.hardware.coolingOFF()
        self.writedatatofile(self.datalog)  # Datenlog schreiben
        self.logger.info(u"Sequenz beendet")


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
        datafile.write("#TargetHeating, CurrentHeating, TargetCooling, CurrentCooling\n")
        for x in datalog:
            datafile.write(("{}, {}, {}, {}\n".format(x[0], x[1], x[2], x[3])))
        datafile.close()
        self.logger.info("Logdatei mit Messdaten wurde erstellt: {}".format(filename))


    def start(self, sequence):
        """
            Funktion zum Starten des Controller Threads.
            Sollte vom Starten-Button aufgerufen werden.

        :param sequence: Sequenz die vom Controller abgelaufen wird.
        """
        self.logger.info("Gestartet")
        t = Thread(target=self.controller, args=(sequence,))
        t.start()
        # t.join()


    def stop(self):
        """
            Funktion zum stoppen des Controller Threads.
            Sollte von einem mögliche Stop-Button aufgerufen werden

        """
        self.running = False
        self.logger.info("Abgebrochen")


if __name__ == '__main__':
    sub = Sublimator()
    currentSequence = sub.sequences[0]
    sub.start(currentSequence)

