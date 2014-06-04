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
#import hardwareAdapter
import datetime
import matplotlib.pyplot as plt


running = True
hardware = None
logger = None
progindex = 0
timer = None
datalog = None
sequences = None

def initLogger():
    """
        Initalisiert den logger der überall, auch in den Untermodulen,
        benutzt werden kann.
        Formatierung und verschiedene Handler für Consolen und Datei Logging werden hier konfiguriert
    """
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    filehandler = logging.FileHandler('main.log')
    filehandler.setLevel(logging.INFO)
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filehandler.setFormatter(formatter)
    consolehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    logger.addHandler(consolehandler)


def counter():
    """
         Zeitzähler für die Programmzeiten

    """
    global progindex
    # Methode die im Timer Thread aufgerufen wird
    progindex += 1


def tempregulator(targetheatingtemp, targetcoolingtemp):
    """
         Funktion, welche die Temperatur reguliert um den Zielwerten zu entsprechen
    :param targetheatingtemp: Zielwert für Heizung
    :param targetcoolingtemp: Zielwert für Kühlung
    """
    temp_delay  = 2 # Temperatur-Delay um weiteres aufheizen über TargetHeatingTemp zu verhindern
    # if hardware.getTemperatureHeating() <= targetheatingtemp - temp_delay:
    #     hardware.heatingON()
    # else:
    #     hardware.heatingOFF()
    # if hardware.getTemperatureCooling() >= targetcoolingtemp:
    #     hardware.coolingON()
    # else:
    #     hardware.coolingOFF()


def controller(currSeq):
    """
        Steuert den Ablauf der Sequenz.
        Ruft mehrmals Timer auf, die entsprechend den Programmpunkten  lange laufen
    :param currSeq:
    """
    global running, progindex,datalog
    # Initalisierungen für den ersten programmpunkt
    progindex = 0
    prog = currSeq.programs[progindex]
    targetheatingtemp = prog.targetHeatingTemp
    targetcoolingtemp = prog.targetCoolingTemp
    timer = Timer(prog.time, counter)
    timer.start()
    oldindex = progindex
    running = True
    datalog = []
    # Schleife die solange läuft, bis die Sequenz komplett durchlaufen ist oder von außen abgebrochen wird.
    while running:
        # Ablauf der Sequenz steuern
        if progindex < len(currSeq.programs) and oldindex != progindex:
            oldindex = progindex
            prog = currSeq.programs[progindex]
            timer = Timer(prog.time, counter)
            timer.start()
            targetheatingtemp = prog.targetHeatingTemp
            targetcoolingtemp = prog.targetCoolingTemp
        #Abbruchbedingung - Ende der Sequenz erreicht
        if progindex == len(currSeq.programs):
            running = False

        # Temperatur regulieren
        tempregulator(targetheatingtemp, targetcoolingtemp)
        # Ausgabe der momentanen Daten
        # logger.debug("Programm {1}: TargetHeatingTemp:{0} CurrentHeatingTemp:{2} TargetCoolingTemp:{3} CurrentCoolingTemp:{4} ".
        #              format(targetheatingtemp, currSeq.name,hardware.getTemperatureHeating(),targetcoolingtemp,hardware.getTemperatureCooling()))
        datalog.append((targetheatingtemp,random.randint(targetheatingtemp/2, targetheatingtemp),targetcoolingtemp,
                        random.randint(targetcoolingtemp/2, targetcoolingtemp)))
        # Pause
        time.sleep(0.3)

    writedatatofile(datalog, currSeq) #Datenlog schreiben
    logger.info(u"Sequenz abgelaufen")


def writedatatofile(datalog, currSeq):
    """
        Schreibt Datenlog in eine .csv Datei um damit weiter arbeiten zu können.
    :param datalog: Der zu schreibende Datenlog
    :param currSeq: Gewählte Sequenz, mit der das Programm abgelaufen ist
    """
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    filename = "./logs/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "_" + currSeq.name + ".csv"
    datafile = open(filename, 'w')
    datafile.write("#TargetHeating, CurrentHeating, TargetCooling, CurrentCooling\n")
    for x in datalog:
        datafile.write(("{}, {}, {}, {}\n".format(x[0], x[1], x[2], x[3])))
    datafile.close()
    logger.info("Logdatei mit Messdaten wurde erstellt: {}".format(filename))


def plotlog(data):
    """
         Plottet die Daten als Temperaturkurve
    :param data: Daten, die vom Controller gesammelt wurden
    """
    fig, ax = plt.subplots()
    ax.plot([x[0] for x in data],'r--')#targetHeating
    ax.plot([x[1] for x in data],'r-')#heating
    ax.plot([x[2] for x in data],'b--')#targetCooling
    ax.plot([x[3] for x in data],'b-')#cooling
    maxTemp = max([x[0] for x in data])
    plt.axis([0, len(data), 0, maxTemp+10]) #xmin,xmax,ymin,ymax
    plt.title("Programmablauf")
    plt.xlabel("Zeit")
    plt.ylabel(u"Temperatur °C")
    plt.show() # !Stoppt den momentanen Thread solange bis Plot geschlossen wird!


def start(sequence):
    """
        Funktion zum Starten des Controller Threads.
        Sollte vom Starten-Button aufgerufen werden.

    :param sequence: Sequenz die vom Controller abgelaufen wird.
    """
    global running, datalog
    logger.info("Gestartet")
    t = Thread(target=controller,args=(sequence,))
    t.start()


def stop():
    """
        Funktion zum stoppen des Controller Threads.
        Sollte von einem mögliche Stop-Button aufgerufen werden

    """
    global running
    running = False
    logger.info("Gestoppt")

def initMain():

    initLogger()

    # Hardware Adapter initalisieren
    # hardware = hardwareAdapter.hardwareAdapter()

    # Import der zur Verfuegung stehenden Sequenzen
    global sequences
    sequences = SequenceHandler.importSequences()

if __name__ == '__main__':
    initMain()
    currentSequence = sequences[0]
    start(currentSequence)

