import glob
import json


class ProgramPart:
    targetTemp = 0
    time = 0
    def __init__(self, temp, time):
        self.targetTemp = temp
        self.time = time


class Sequence:
    name = ""
    programs = []

    def __init__(self,name,programs):
        self.name = name
        self.programs = programs


def importSequences():
    """
    Importiert Sequenzen aus dem Unterordner /sequences/

    :rtype : [Sequence]
    :return: Liste von Sequence Objekten
    """
    sequences = []
    for filename in glob.iglob("./sequences/*.seq"):
        sequencefile = open(filename)
        data = json.load(sequencefile)
        programs = []
        for programPartObject in data["Sequenz"]:
            part = ProgramPart(programPartObject["Temp"],programPartObject["Time"])
            programs.append(part)
        newSequence = Sequence(data["Name"],programs)
        sequences.append(newSequence)
    return sequences


def saveSequenceToFile(sequence):
    """
    Speichert Sequenz im /sequence/ Ordner
    :param sequence: Sequence Object
    """
    pass