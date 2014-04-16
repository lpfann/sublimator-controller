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

    def __init__(self, name, programs):
        self.name = name
        self.programs = programs



def jdefault(o):
    return o.__dict__


def importSequences():
    """
    Importiert Sequenzen aus dem Unterordner /sequences/

    :rtype : [Sequence]
    :return: Liste von Sequence Objekten
    """
    sequences = []
    for filename in glob.iglob("./sequences/*.seq"):
        with open(filename) as sequencefile:
            data = json.load(sequencefile)
            programs = []
            for programPartObject in data["programs"]:
                part = ProgramPart(programPartObject["targetTemp"], programPartObject["time"])
                programs.append(part)
            newSequence = Sequence(data["name"], programs)
            sequences.append(newSequence)
    return sequences


def saveSequenceToFile(sequence):
    """
    Speichert Sequenz im /sequence/ Ordner
    :param sequence: Sequence Object
    """
    name = sequence.name
    fileExisting = glob.glob("./sequences/"+name+".seq")
    if len(fileExisting) > 0:
        print("File" + name + "already existing")
    else:
        with open("./sequences/"+name+".seq", 'w', encoding="UTF-8") as f:
            json.dump(sequence, f, default=jdefault, indent=2)

