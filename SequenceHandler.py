import glob
import json
import logging


logger = logging.getLogger("Sublimator")

class ProgramPart:

    def __init__(self, heatingtemp,coolingtemp, time):
        self.targetHeatingTemp = heatingtemp
        self.targetCoolingTemp = coolingtemp
        self.time = time



class Sequence:
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
            try:
                data = json.load(sequencefile)
            except:
                logger.error("Sequenzdatei {} konnte nicht eingelesen werden. Falsches Format!".format(filename))
                continue

            programs = []
            for programPartObject in data["programs"]:
                part = ProgramPart(programPartObject["targetHeatingTemp"],programPartObject["targetCoolingTemp"], programPartObject["time"])
                programs.append(part)
            newSequence = Sequence(data["name"], programs)
            sequences.append(newSequence)

    logger.debug("%i Sequenzen konnten importiert werden" % len(sequences))
    return sequences


def saveSequenceToFile(sequence):
    """
    Speichert Sequenz im /sequence/ Ordner
    :param sequence: Sequence Object
    """
    name = sequence.name
    fileExisting = glob.glob("./sequences/"+name+".seq")
    if len(fileExisting) == 0:
        with open("./sequences/"+name+".seq", 'w', encoding="UTF-8") as f:
            json.dump(sequence, f, default=jdefault, indent=2)
    else:
        logger.error("Datei %s exisitert schon. Konnte nicht gespeichert werden"%(name+".seq"))
