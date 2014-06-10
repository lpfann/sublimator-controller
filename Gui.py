import _tkinter
from Tkinter import *
import SequenceHandler
import Sublimator
import time
from threading import Timer
import datetime
import sys
#import matplotlib
#matplotlib.use('TkAgg')    # Ist die Zeile noetig? Bei mir sagt er die waere redundant.
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.backend_bases import key_press_handler
#from matplotlib.figure import Figure


class Gui(Frame):


    def __init__(self, master=None):
        self.coolinglist = []
        self.heatinglist = []
        self.timelist = []
        self.seplist = []
        self.running = FALSE
        self.runner = 1
        Frame.__init__(self, master)
        self.sequences = SequenceHandler.importSequences()
        self.grid()
        self.showText()
        self.showTextline(0)
        self.buttonCreate()
        self.button2Create()


    def showTextline(self, sequence):

        phases = Entry(self)
        phases.insert(END,"Phases of Program")
        phases.grid(column=0,row=1,sticky=N)
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

                tlinefree.insert(END,"Phase " + str(i+1))
                tlinefree.grid(column=0,row=t,sticky=N)
                tlinefree.config(state=(DISABLED))
                self.seplist.append(tlinefree)

                tlineheat.config(state=NORMAL)
                tlineheat.insert(END,"Heating: " + str(self.sequences[0].programs[i].targetHeatingTemp) + " Celsius")
                tlineheat.grid(column=0,row = t+1,sticky=N)
                tlineheat.config(state=DISABLED)
                self.heatinglist.append(tlineheat)

                tlinecool.config(state=NORMAL)
                tlinecool.insert(END,"Cooling: " + str(self.sequences[0].programs[i].targetCoolingTemp) + " Celsius")
                tlinecool.grid(column=0,row = t+2,sticky=N)
                tlinecool.config(state=DISABLED)
                self.coolinglist.append(tlinecool)


                tlinetime.config(state=NORMAL)
                tlinetime.insert(END,"time: " + str(self.sequences[0].programs[i].time) + " Sekunden")
                tlinetime.grid(column=0,row = t+3,sticky=N)
                tlinetime.config(state=DISABLED)
                self.timelist.append(tlinetime)

                t+=4

    def counter(self):
        """
         Zeitzaehler fuer die Programmzeiten
        """

        # Methode die im Timer Thread aufgerufen wird
        self.progindex += 1

    def showText(self):
        self.scrollbar = Scrollbar(self)
        self.test = Text(self,height=10,width=120)
        self.scrollbar.grid(column=3,row=0,sticky=N+S)
        self.test.grid(column=2,row=0)
        self.scrollbar.config(command=self.test.yview)
        self.test.config(yscrollcommand=self.scrollbar.set,state=DISABLED)


#def showDiagram(self):
   #     self.canvas = FigureCanvasTkAgg()
    #    self.canvas.show()
     #   self.canvas.get_tk_widget().grid(row = 3,column = 2,sticky = S+W)
      #  toolbar = NavigationToolbar2TkAgg( self.canvas)
       # toolbar.update()
        #self.canvas._tkcanvas.grid(row = 3, column = 3, sticky = S+W)



    def buttonCreate(self):
        self.button01 = Button(self)

        self.button01["text"] = self.sequences[0].name
        self.button01.bind("<Button-1>",self.button01_Click)
        self.button01.grid(column=0,row=0,sticky=W+E)


    def button2Create(self):
        self.button02 = Button(self)
        self.button02["text"] = "starten"
        programm = Label(text="Waehle Programm aus \n und starte dieses!")
        self.button02.bind("<Button-1>",self.button02_Click)
        self.button02.grid(column=1,row=0,sticky=W)
        programm.grid(column=1,row=0,sticky=W)


    def button01_Click(self,event):

        if len(self.sequences) > 1:

           if(self.runner < len(self.sequences)):
                self.button01["text"] = self.sequences[self.runner].name
                self.showTextline(self.runner)
                self.runner+=1
           else:
               self.showTextline(0)
               self.button01["text"] = self.sequences[0].name
               self.runner = 1

    def button02_Click(self,event):

        if self.running == False:
            self.running = True
            self.progindex = 0
            prog = self.sequences[self.runner-1].programs[self.progindex]
            targetheatingtemp = prog.targetHeatingTemp
            targetcoolingtemp = prog.targetCoolingTemp

            self.test.config(state=NORMAL)
            self.test.delete(0.0,END)
            self.test.insert(END,"Program starts \n")

            Sublimator.start(self.sequences[self.runner-1])
            timer = Timer(prog.time, self.counter)
            timer.start()
            oldindex = self.progindex

            while Sublimator.running:
                if self.progindex < len(self.sequences[self.runner-1].programs) and oldindex != self.progindex:
                    oldindex = self.progindex
                    prog = self.sequences[self.runner-1].programs[self.progindex]
                    timer = Timer(prog.time, self.counter)
                    timer.start()
                    targetheatingtemp = prog.targetHeatingTemp
                    targetcoolingtemp = prog.targetCoolingTemp
        #Abbruchbedingung - Ende der Sequenz erreicht
                if self.progindex == len(self.sequences[self.runner-1].programs):
                    running = False
                 # Pause
                self.test.insert(END,"Programm {1}: TargetHeatingTemp:{0} CurrentHeatingTemp:{2} TargetCoolingTemp:{3} CurrentCoolingTemp:{4} ".
                      format(targetheatingtemp, self.sequences[self.runner-1].name,10,targetcoolingtemp,10) + "\n")
                time.sleep(0.3)
            else:
                self.test.insert(END,"Program done!\n")

            self.test.config(state=DISABLED)
            if self.scrollbar.get()[1] == 1.0:
                self.test.yview(END)
            self.running = False

# create the application
Sublimator.initMain()

myapp = Gui()

#
# here are method calls to the window manager class
#

myapp.master.title("Sublimator")
myapp.master.minsize(860,560)
myapp.mainloop()