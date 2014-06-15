import logging
from Tkinter import *
import SequenceHandler
import Sublimator
import time
from threading import Timer
import datetime
import sys
import matplotlib

matplotlib.use('TkAgg')  # Ist die Zeile noetig? Bei mir sagt er die waere redundant.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class WidgetLogger(logging.Handler):
    '''
    Erlaubt es, die Konsolenausgabe in einem Widget anzuzeigen
    '''

    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')

    def emit(self, record):
        r = self.format(record)
        self.widget.configure(state=NORMAL)
        self.widget.insert(END, r)
        self.widget.configure(state=DISABLED)


class Gui(Frame):
    def __init__(self, master=None):
        self.coolinglist = []
        self.heatinglist = []
        self.timelist = []
        self.seplist = []
        self.running = FALSE
        self.runner = 1
        self.sequences = Sublimator.sequences
        Frame.__init__(self, master)
        self.grid()
        self.showText()
        self.showTextline(0)
        self.buttonCreate()
        self.button2Create()
        self.showDiagram()


    def showTextline(self, sequence):

        phases = Entry(self)
        phases.insert(END, "Phases of Program")
        phases.grid(column=0, row=1, sticky=N)
        phases.config(state=DISABLED)
        t = 2
        for heat in self.heatinglist:
            heat.destroy()
        self.heatinglist[:] = []
        for time in self.timelist:
            time.destroy()
        self.timelist[:] = []
        for cool in self.coolinglist:
            cool.destroy()
        self.coolinglist[:] = []
        for sep in self.seplist:
            sep.destroy()
        self.seplist[:] = []

        for i in range(len(self.sequences[sequence].programs)):
            tlineheat = Entry(self)
            tlinecool = Entry(self)
            tlinetime = Entry(self)
            tlinefree = Entry(self)

            tlinefree.insert(END, "Phase " + str(i + 1))
            tlinefree.grid(column=0, row=t, sticky=N)
            tlinefree.config(state=(DISABLED))
            self.seplist.append(tlinefree)

            tlineheat.config(state=NORMAL)
            tlineheat.insert(END, "Heating: " + str(self.sequences[0].programs[i].targetHeatingTemp) + " Celsius")
            tlineheat.grid(column=0, row=t + 1, sticky=N)
            tlineheat.config(state=DISABLED)
            self.heatinglist.append(tlineheat)

            tlinecool.config(state=NORMAL)
            tlinecool.insert(END, "Cooling: " + str(self.sequences[0].programs[i].targetCoolingTemp) + " Celsius")
            tlinecool.grid(column=0, row=t + 2, sticky=N)
            tlinecool.config(state=DISABLED)
            self.coolinglist.append(tlinecool)

            tlinetime.config(state=NORMAL)
            tlinetime.insert(END, "time: " + str(self.sequences[0].programs[i].time) + " Sekunden")
            tlinetime.grid(column=0, row=t + 3, sticky=N)
            tlinetime.config(state=DISABLED)
            self.timelist.append(tlinetime)

            t += 4


    def showText(self):
        self.scrollbar = Scrollbar(self)
        self.test = Text(self, height=10, width=120)
        logger = logging.getLogger()
        logger.addHandler(WidgetLogger(self.test))
        self.scrollbar.grid(column=3, row=0, sticky=N + S)
        self.test.grid(column=2, row=0)
        self.scrollbar.config(command=self.test.yview)
        self.test.config(yscrollcommand=self.scrollbar.set, state=DISABLED)


    def showDiagram(self):
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        a.plot([0], [0])
        self.canvas = FigureCanvasTkAgg(f,self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        self.canvas._tkcanvas.grid(column=2, row=1)


    def buttonCreate(self):
        self.button01 = Button(self)

        self.button01["text"] = self.sequences[0].name
        self.button01.bind("<Button-1>", self.button01_Click)
        self.button01.grid(column=0, row=0, sticky=W + E)


    def button2Create(self):
        self.button02 = Button(self)
        self.button02["text"] = "Start"
        programm = Label(text="Waehle Programm aus \n und starte dieses!")
        self.button02.bind("<Button-1>", self.button02_Click)
        self.button02.grid(column=1, row=0, sticky=W)
        programm.grid(column=1, row=0, sticky=W)


    def button01_Click(self, event):

        if len(self.sequences) > 1:

            if (self.runner < len(self.sequences)):
                self.button01["text"] = self.sequences[self.runner].name
                self.showTextline(self.runner)
                self.runner += 1
            else:
                self.showTextline(0)
                self.button01["text"] = self.sequences[0].name
                self.runner = 1

    def button02_Click(self, event):

        if not Sublimator.running:
            Sublimator.start(self.sequences[self.runner - 1])
            self.button02.config(text="Stop")

            if self.scrollbar.get()[1] == 1.0:
                self.test.yview(END)
        else:
            Sublimator.stop()
            self.button02.config(text="Start")




if __name__ == '__main__':
    Sublimator.initMain()
    myapp = Gui()

    myapp.master.title("Sublimator")
    myapp.master.minsize(860, 560)
    myapp.mainloop()