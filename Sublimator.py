#!/usr/bin/env python2
# coding=utf-8
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries
import random
import time
from threading import Timer
import logging
import SequenceHandler
#import hardwareAdapter
import datetime
import matplotlib.pyplot as plt

running = False
hardware = None
logger = None
progindex = 0


def initLogger():
    global logger
    #Logger initalisieren
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
    global progindex
    # Methode die im Timer Thread aufgerufen wird
    progindex += 1


def tempregulator(targetheatingtemp, targetcoolingtemp):
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
    global running, progindex
    progindex = 0
    prog = currSeq.programs[progindex]
    targetheatingtemp = prog.targetHeatingTemp
    targetcoolingtemp = prog.targetCoolingTemp
    Timer(prog.time, counter).start()
    oldindex = progindex
    running = True
    datalog = []
    while (running):
        # Ablauf der Sequenz steuern
        if progindex < len(currSeq.programs) and oldindex != progindex:
            oldindex = progindex
            prog = currSeq.programs[progindex]
            Timer(prog.time, counter).start()
            targetheatingtemp = prog.targetHeatingTemp
            targetcoolingtemp = prog.targetCoolingTemp

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

    writedata(datalog, currSeq)
    plotlog(datalog)
    logger.info("Sequenz vollständig")


def writedata(datalog, currSeq):
    filename = "./logs/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "_" + currSeq.name + ".csv"
    datafile = open(filename, 'w+')
    datafile.write("#TargetHeating, CurrentHeating, TargetCooling, CurrentCooling\n")
    for x in datalog:
        datafile.write(("{}, {}, {}, {}\n".format(x[0], x[1], x[2], x[3])))
    datafile.close()
    logger.info("Logdatei mit Messdaten wurde erstellt: {}".format(filename))


def plotlog(data):
    fig, ax = plt.subplots()
    ax.plot([x[0] for x in data],'r--')#targetHeating
    ax.plot([x[1] for x in data],'r-', antialiased=True)#heating
    ax.plot([x[2] for x in data],'b--')#targetCooling
    ax.plot([x[3] for x in data],'b-')#cooling
    maxTemp = max([x[0] for x in data])
    plt.axis([0, len(data), 0, maxTemp+10]) #xmin,xmax,ymin,ymax
    plt.title("Programmablauf")
    plt.xlabel("Zeit")
    plt.ylabel(u"Temperatur °C")
    plt.show()



def start():
    logger.info("Gestartet")
    pass


def stop():
    global running
    running = False
    logger.info("Gestoppt")


if __name__ == '__main__':
    initLogger()
    # Hardware Adapter initalisieren
    #hardware = hardwareAdapter.hardwareAdapter()
    # Import der zur Verfuegung stehenden Sequenzen
    sequences = SequenceHandler.importSequences()
    currentSequence = sequences[0]
    controller(currentSequence)

