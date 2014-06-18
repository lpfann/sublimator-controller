# coding=utf-8
import logging
from Tkinter import *
from matplotlib.figure import Figure
import Sublimator
import matplotlib
import numpy as np

MAX_NUM_PLOTDATA = 100

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import pyplot as plt


class Gui(Frame):

    def __init__(self, master=None):
        self.coolinglist = []
        self.heatinglist = []
        self.timelist = []
        self.seplist = []
        self.running = FALSE    
        self.log = []
        self.sequences = Sublimator.sequences
	self.testsequence = [x.name for x in self.sequences]
        self.variable = StringVar(master)
        self.variable.set(self.sequences[0].name)
	self.runner = 0
	
	Frame.__init__(self, master)
        self.grid()
	self.buttoncontainer = Frame(master=self,bg="red")
	self.buttoncontainer.grid(column = 0, row = 0)
	
	self.container1()
        self.showText()
        self.showTextline(event=None)
        self.buttonCreate()
        self.button2Create()
        self.showDiagram()
        self.saveProgram()
        
    def container1(self):
	self.containercan = Canvas(self, borderwidth=0, background="red")
        self.infocontainer = Frame(self.containercan, background="green")
        self.vsb = Scrollbar(self.containercan, orient="vertical", command=self.containercan.yview)
        self.containercan.configure(yscrollcommand=self.vsb.set)
	self.containercan.grid(column = 0, row = 2)
	self.infocontainer.pack(side="left",fill="both")
	self.vsb.pack(side="right",fill="y")
	
    def showText(self):
        self.scrollbar = Scrollbar(self)
        self.textField = Text(self, height=10, width=90)
        self.scrollbar.grid(column=3, row=0, sticky=N + S)
        self.textField.grid(column=2, row=0)
        self.scrollbar.config(command=self.textField.yview)
        self.textField.config(
            yscrollcommand=self.scrollbar.set, state=DISABLED)

    def buttonCreate(self):
        
        
        self.dropdown = apply(OptionMenu, (self.buttoncontainer, self.variable) + tuple(self.testsequence))
        self.dropdown.bind("<<MenuSelect>>", self.showTextline)
        self.dropdown.grid(column = 0, row = 0, sticky = W+E) 
        

    def button2Create(self):
        self.button02 = Button(self.buttoncontainer)
        self.button02["text"] = "Start"
        self.button02.bind("<Button-1>", self.button02_Click)
        self.button02.grid(column=1, row=0, sticky=W)

    def saveProgram(self):
        self.saveProg = Button(self.buttoncontainer)
        self.saveProg["text"] = "new Program"
        self.saveProg.bind("<Button-1>", self.saveProgEvent)
        self.saveProg.grid(column=0, row=1, sticky=E)

    def button02_Click(self, event):

        if not Sublimator.running:
            Sublimator.start(self.sequences[self.runner])
            self.plotData = [(0, 0, 0, 0)] * MAX_NUM_PLOTDATA
            self.button02.config(text="Stop")

            if self.scrollbar.get()[1] == 1.0:
                self.textField.yview(END)

        else:
            Sublimator.stop()
            self.button02.config(text="Start")
	   
    def showTextline(self, event):
	self.runner = self.testsequence.index(self.variable.get())
        phases = Entry(self.infocontainer)
        phases.insert(END, "Phases of Program")
        phases.grid(column=0, row=0, sticky=N)
        phases.config(state=DISABLED)
        t = 0
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

        for i in range(len(self.sequences[self.runner].programs)):
            tlineheat = Entry(self.infocontainer)
            tlinecool = Entry(self.infocontainer)
            tlinetime = Entry(self.infocontainer)
            tlinefree = Entry(self.infocontainer)

            tlinefree.insert(END, "Phase " + str(i + 1))
            tlinefree.grid(column=0, row=t, sticky=N)
            tlinefree.config(state=(DISABLED))
            self.seplist.append(tlinefree)

            tlineheat.config(state=NORMAL)
            tlineheat.insert(
                END, "Heating: " + str(self.sequences[self.runner].programs[i].targetHeatingTemp) + " Celsius")
            tlineheat.grid(column=0, row=t + 1, sticky=N)
            tlineheat.config(state=DISABLED)
            self.heatinglist.append(tlineheat)

            tlinecool.config(state=NORMAL)
            tlinecool.insert(
                END, "Cooling: " + str(self.sequences[self.runner].programs[i].targetCoolingTemp) + " Celsius")
            tlinecool.grid(column=0, row=t + 2, sticky=N)
            tlinecool.config(state=DISABLED)
            self.coolinglist.append(tlinecool)

            tlinetime.config(state=NORMAL)
            tlinetime.insert(
                END, "time: " + str(self.sequences[self.runner].programs[i].time) + " Sekunden")
            tlinetime.grid(column=0, row=t + 3, sticky=N)
            tlinetime.config(state=DISABLED)
            self.timelist.append(tlinetime)

            t += 4   

    def saveProgEvent(self, event):
        def buttonClose():
            saveWindow.quit()

        saveWindow = Toplevel()
        saveWindow.title("Save Program")
        text = """{
 "name": (programname),
 "programs": [
   {
     "targetHeatingTemp": (temp),
     "targetCoolingTemp": (temp),
     "time": (time)
   },
   {
     "targetHeatingTemp": (temp),
     "targetCoolingTemp": (temp),
     "time": (time)
   },
   {
     "targetHeatingTemp": (temp),
     "targetCoolingTemp": (temp),
     "time": (time)
   },
   {
      "targetHeatingTemp": (temp),
      "targetCoolingTemp": (temp),
      "time": (time)
    }
  ] 
}"""

        def buttonSave():
            saveData = Text(master=saveWindow)
            dataScrollbar = Scrollbar(master=saveWindow)
            dataScrollbar.grid(column=0, row=0, sticky=N + S)
            saveData.insert(END, text)
            saveData.grid(column=1, row=0)
            dataScrollbar.config(command=saveData.yview)
            saveData.config(yscrollcommand=dataScrollbar.set)

            saveButton = Button(master=saveWindow)
            saveButton["text"] = "save"
            saveButton.bind("<Button-1>", buttonSave)
            saveButton.grid(column=0, row=1)

    def showDiagram(self):
        self.plotData = [(0, 0, 0, 0)] * MAX_NUM_PLOTDATA
        self.fig, self.ax = plt.subplots()
        self.ax2 = self.ax.twinx()
        self.line1, = self.ax.plot(
            [x[0] for x in self.plotData], 'r--')  # Target Heat
        self.line2, = self.ax.plot([x[1] for x in self.plotData], 'r-')  # Heat
        self.line3, = self.ax2.plot(
            [x[2] for x in self.plotData], 'b--')  # Target Cooling
        self.line4, = self.ax2.plot(
            [x[3] for x in self.plotData], 'b-')  # Cooling
        self.ax.set_ylim([0, 160])
        self.ax2.set_ylim([0, 30])

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid()
        self.canvas._tkcanvas.grid(column=2, row=1, rowspan=100, sticky=W + S)

    def updatePlot(self):
        if Sublimator.running:
            data = Sublimator.datalog

            # heatTempData = [x[1] for x in data]
            # ymin = float(min(heatTempData)) - 10
            # ymax = float(max(heatTempData)) + 10
            # self.ax.set_ylim(ymin, ymax)

            self.plotData = data
            if len(data) > MAX_NUM_PLOTDATA:
                self.plotData = data
                del self.plotData[0: len(data) - MAX_NUM_PLOTDATA]

            self.line1.set_xdata(np.arange(len(self.plotData)))
            self.line1.set_ydata([x[0] for x in self.plotData])

            self.line2.set_xdata(np.arange(len(self.plotData)))
            self.line2.set_ydata([x[1] for x in self.plotData])

            self.line3.set_xdata(np.arange(len(self.plotData)))
            self.line3.set_ydata([x[2] for x in self.plotData])

            self.line4.set_xdata(np.arange(len(self.plotData)))
            self.line4.set_ydata([x[3] for x in self.plotData])

            # TODO: Eventuell Blitting einbauen um Performance zu verbessern

            # self.ax.plot()
            # self.ax2.plot()
            self.fig.canvas.draw()

        self.after(1000, self.updatePlot)
        if not Sublimator.running:
            self.button02.config(text="Start")

    def updateConsole(self):
        '''
        Updatet die Konsolenausgabe.
        Verhindert Probleme mit Multithrading und Tkinter...
        '''

        self.textField.configure(state=NORMAL)
        self.textField.delete(1.0, END)
        self.log = Sublimator.log_capture_string.getvalue()
        self.textField.insert(END, self.log)
        self.textField.configure(state=DISABLED)
        self.after(1000, self.updateConsole)


def _quit():
    '''
    Sorgt dafür das alle Threads in Tkinter und matplotlib richtig geschlossen werden
    :return:
    '''
    root.quit()
    root.destroy()


if __name__ == '__main__':
    Sublimator.initMain()
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", _quit)
    myapp = Gui(root)

    myapp.master.title("Sublimator")
    myapp.master.minsize(860, 560)
    myapp.after(300, myapp.updatePlot)
    myapp.after(1000, myapp.updateConsole)
    myapp.mainloop()
