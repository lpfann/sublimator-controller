#!/usr/bin/env python2
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries 

import SequenceHandler
import hardwareAdapter
import time
from threading import Timer

progindex = 0
targettemp = 0
running = False


def counter():
    global progindex
    progindex += 1


def tempregulator():
    global targettemp
    if targettemp <= hardware.getTemparature():
        hardware.heatingON()
    else:
        hardware.heatingOFF()



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
        if progindex == len(currSeq.programs):
            running = False
        # Ausgabe der momentanen Daten
        print "Sequenz {1}: TargetTemp:{0} CurrentTemp: - Timer: ".format(targettemp, currSeq.name)
        # Temperatur regulieren
        tempregulator()
        # Pause
        time.sleep(0.3)



def start():
    pass


def stop():
    running = False


if __name__ == '__main__':
    global hardware
    # Import der zur Verfuegung stehenden Sequenzen
    sequences = SequenceHandler.importSequences()
    currentSequence = sequences[0]
    controller(currentSequence)
    # Hardware Adapter initalisieren
    hardware = hardwareAdapter.hardwareAdapter()

