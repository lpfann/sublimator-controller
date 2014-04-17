#!/usr/bin/env python2
# coding=utf-8
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries 

import time
from threading import Timer
import logging
import SequenceHandler
#import hardwareAdapter


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


def tempregulator(targettemp):
    # if targettemp <= hardware.getTemperatureHeating():
    #     hardware.heatingON()
    # else:
    #     hardware.heatingOFF()
    pass

def controller(currSeq):
    global running, progindex
    progindex = 0
    prog = currSeq.programs[progindex]
    targettemp = prog.targetTemp
    Timer(prog.time, counter).start()
    oldindex = progindex
    running = True
    while (running):
        # Ablauf der Sequenz steuern
        if progindex < len(currSeq.programs) and oldindex != progindex:
            oldindex = progindex
            prog = currSeq.programs[progindex]
            Timer(prog.time, counter).start()
            targettemp = prog.targetTemp
            # Ausgabe der momentanen Daten
            logger.debug("Sequenz {1}: TargetTemp:{0} CurrentTemp: - Timer: ".format(targettemp, currSeq.name))
        if progindex == len(currSeq.programs):
            running = False
        # Temperatur regulieren
        tempregulator(targettemp)
        # Pause
        time.sleep(0.3)
    logger.info("Sequenz vollständig")


def start():
    logger.info("Gestartet")
    pass


def stop():
    global running
    running = False
    logger.info("Gestoppt")


if __name__ == '__main__':
    initLogger()
    # Import der zur Verfuegung stehenden Sequenzen
    sequences = SequenceHandler.importSequences()
    currentSequence = sequences[0]
    controller(currentSequence)
    # Hardware Adapter initalisieren
    #hardware = hardwareAdapter.hardwareAdapter()

