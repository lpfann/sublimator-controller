#!/usr/bin/env python2
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries 

import SequenceHandler
#import hardwareAdapter
import time
from threading import Timer

def controller():
    Timer(1, controller ).start()


def start():
    pass

def stop():
    pass


if __name__ == '__main__':

    # Import der zur Verfügung stehenden Sequenzen
    sequences = SequenceHandler.importSequences()

    # Hardware Adapter initalisieren
    #hardware = hardwareAdapter.hardwareAdapter()

