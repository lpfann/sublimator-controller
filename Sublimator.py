#!/usr/bin/env python2
# coding=utf-8
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries 

import SequenceHandler
#import hardwareAdapter
import time
from threading import Timer
import logging



progindex = 0
targettemp = 0
running = False

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
    progindex += 1


def tempregulator():
    global targettemp
    # if targettemp <= hardware.getTemparature():
    #     hardware.heatingON()
    # else:
    #     hardware.heatingOFF()



def controller(currSeq):
    global progindex, targettemp, running
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
            logger.debug("Sequenz {1}: TargetTemp:{0} CurrentTemp: - Timer: ".format(targettemp, currSeq.name))
        if progindex == len(currSeq.programs):
            running = False
        # Ausgabe der momentanen Daten
        # Temperatur regulieren
        tempregulator()
        # Pause
        time.sleep(0.3)
    logger.info("Sequenz vollständig")


def start():
    logger.info("Gestartet")
    pass


def stop():
    running = False
    logger.info("Gestoppt")


if __name__ == '__main__':
    global hardware
    # Import der zur Verfuegung stehenden Sequenzen
    sequences = SequenceHandler.importSequences()
    currentSequence = sequences[0]
    controller(currentSequence)
    # Hardware Adapter initalisieren
    #hardware = hardwareAdapter.hardwareAdapter()

