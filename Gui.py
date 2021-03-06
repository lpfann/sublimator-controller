# coding=utf-8
from Tkinter import *
import Sublimator
import matplotlib
import numpy as np
import datetime

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
MAX_NUM_PLOTDATA = 100


class CalibrationDialog:

    '''
        Dialog for Calibrating the lightbarrier for the current light conditions.
    '''

    def __init__(self, parent,sublimator):
        self.sublimator = sublimator
        top = self.top = Toplevel(parent)
        self.parent = parent
        Label(
            top, text="Calibration in progress.\n Lightsensor will not work if canceled.").pack()
        self.timelabel = Label(top, text="Time: 0:0")
        self.timelabel.pack()
        self.startTime = datetime.datetime.utcnow()
        self.calibrationRunning = True
        self.finishbutton = Button(top, text="Cancel Calibration", command=self.finish,foreground="red")
        self.finishbutton.pack(pady=5)

        top.wait_visibility()
        top.protocol('WM_DELETE_WINDOW', self.finish)
        # start calibration thread
        self.sublimator.calib_start()
        self.updateTime()

    def finish(self):
        # stopping calibr. thread
        self.sublimator.calib_stop()
        self.calibrationRunning = False
        self.top.destroy()

    def updateTime(self):
        if self.calibrationRunning:
            self.passedTime = datetime.datetime.utcnow() - self.startTime
            self.timelabel.config(
                text="Calibration-Time: {}:{}".format(self.passedTime.seconds / 60, self.passedTime.seconds % 60))
            if self.sublimator.hardware.activeConfiguration():
                self.parent.after(1000, self.updateTime)
            else:
                self.sublimator.lightcalibrationFinished = True
                self.finishbutton.config(text="Finish", foreground="black")
                self.timelabel.config(
                    text="Calibration finished!")


class Gui(Frame):

    '''
    Main Window for controlling the underlying program.
    '''

    def __init__(self, sublimator, master=None):
        self.sublimator = sublimator
        self.coolinglist = []
        self.heatinglist = []
        self.timelist = []
        self.seplist = []
        self.log = []

        self.progend = True
        self.sequences = self.sublimator.sequences
        self.testsequence = [x.name for x in self.sequences]
        self.variable = StringVar(master)
        self.variable.set(self.sequences[0].name)
        self.runner = 0
        self.oldlen = 0

        Frame.__init__(self, master)

        self.grid()
        self.buttoncontainer = Frame(master=self)
        self.buttoncontainer.grid(column=0, row=0)

        self.infoContainer()
        self.showText()
        self.showTextline(event=None)
        self.createDropdown()
        self.createStartButton()
        self.createCalibrationButton()
        self.showDiagram()
        self.saveDiagram()

    def infoContainer(self):
        '''
            Erstellt Container fuer die Programminformationen und setzt eine Scrollbar ein.
            '''
        self.containercan = Canvas(self, borderwidth=0, width=30)
        self.infocontainer = Frame(self.containercan)
        self.vsb = Scrollbar(self, orient="vertical", command=self.containercan.yview)
        self.containercan.configure(yscrollcommand=self.vsb.set)
        self.containercan.grid(column=0, row=2, sticky=N + S + E)
        self.vsb.grid(column=1, row=2, sticky=N + S)
        interior_id = self.containercan.create_window(
            (0, 0), window=self.infocontainer, anchor="nw")

        def _configure_infocontainer(event):
            # update the scrollbars to match the size of the inner frame
            size = (self.infocontainer.winfo_reqwidth(), self.infocontainer.winfo_reqheight())
            self.containercan.config(scrollregion="0 0 %s %s" % size)
            if self.infocontainer.winfo_reqwidth() != self.containercan.winfo_width():
                # update the self.containercan's width to fit the inner frame
                self.containercan.config(width=self.infocontainer.winfo_reqwidth())

        def _configure_containercan(event):
            if self.infocontainer.winfo_reqwidth() != self.containercan.winfo_width():
                # update the inner frame's width to fill the self.containercan
                self.containercan.itemconfigure(interior_id, width=self.containercan.winfo_width())

        self.infocontainer.bind('<Configure>', _configure_infocontainer)
        self.containercan.bind('<Configure>', _configure_containercan)

    def showText(self):
        '''
            Erstellt das Textfenster fuer die Log informationen.
            '''
        self.scrollbar = Scrollbar(self)
        self.textField = Text(self, height=10, width=90)
        self.scrollbar.grid(column=3, row=0, sticky=N + S)
        self.textField.grid(column=2, row=0)
        self.scrollbar.config(command=self.textField.yview)
        self.textField.config(
            yscrollcommand=self.scrollbar.set, state=DISABLED)

    def createDropdown(self):
        '''
        Erstellt das Dropdownmenue fuer die Auswahl der Programme.
        '''
        self.dropdown = apply(
            OptionMenu, (self.buttoncontainer, self.variable) + tuple(self.testsequence))
        self.variable.trace("w", self.showTextline)
        self.dropdown.grid(column=0, row=0, sticky=E + W + N + S)

    def createStartButton(self):
        '''
            Erstellt den Startbutton
            '''
        self.startButton = Button(self.buttoncontainer)
        self.startButton["text"] = "Start"
        self.startButton.bind("<Button-1>", self.startButton_Click)
        self.startButton.grid(column=1, row=0, sticky=E + W + N + S)

    def createCalibrationButton(self):
        '''
        Erstellt den Kalibrierungsbutton
        '''
        self.calibrationButton = Button(self.buttoncontainer)
        self.calibrationButton["text"] = "Lichtschranke kalibrieren"
        self.calibrationButton.bind("<Button-1>", self.calibrateButton_Click)
        self.calibrationButton.grid(column=0, row=2, sticky=E + W + N + S)

    def saveDiagram(self):
        self.checkvariable = IntVar()
        self.saveCheckbox = Checkbutton(
            self.buttoncontainer, text="save Diagram", variable=self.checkvariable)
        self.saveCheckbox.grid(column=0, row=1, sticky=E + W + N + S, columnspan=2)

    def startButton_Click(self, event):
        if not self.sublimator.running:
            self.sublimator.start(self.sequences[self.runner])
            self.plotData = [(0, 0, 0, 0)] * MAX_NUM_PLOTDATA
            self.startButton.config(text="Stop")
            self.saveCheckbox.configure(state="disabled")
        else:
            self.sublimator.stop()
            self.startButton.config(text="Start")
            self.saveCheckbox.configure(state="normal")

    def calibrateButton_Click(self, event):
        dialog = CalibrationDialog(root,self.sublimator)
        dialog.top.transient(self.master)
        dialog.top.grab_set()
        self.wait_window(dialog.top)
        self.calibTime = dialog.passedTime
        dialog.top.grab_release()
        self.sublimator.logger.info("Light-Calibration was running for {} minutes and {} seconds.".format(
            self.calibTime.seconds / 60, self.calibTime.seconds % 60))

    def showTextline(self, event, *args):
        '''
            sorgt fuer das fuellen des Informationscontainers bei Auswahl von Programm.
            '''
        self.runner = self.testsequence.index(self.variable.get())
        phases = Entry(self.infocontainer)
        phases.insert(END, "Phases of Program")
        phases.grid(column=0, row=0, sticky=N)
        phases.config(state=DISABLED)
        t = 0
        for heat in self.heatinglist:
            heat.destroy()
        self.heatinglist[:] = []
        for time_entry in self.timelist:
            time_entry.destroy()
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
            tlinefree.config(state=(DISABLED), disabledbackground="white")
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

    def button02_Click(self, event):

        if not self.sublimator.running:
            self.sublimator.start(self.sequences[self.runner - 1])
            self.plotData = [(0, 0, 0, 0)] * MAX_NUM_PLOTDATA
            self.button02.config(text="Stop")

            if self.scrollbar.get()[1] == 1.0:
                self.textField.yview(END)

        else:
            self.sublimator.stop()
            self.button02.config(text="Start")

    def showDiagram(self):
        self.plotData = [(0, 0, 0, 0, 0)] * MAX_NUM_PLOTDATA
        self.fig, self.ax = plt.subplots()
        self.ax2 = self.ax.twinx()

        # Lightbarrier Axis
        self.lightax = self.ax.twinx()
        self.fig.subplots_adjust(right=0.75)
        # Move lightbarrier axis to the right
        self.lightax.spines['right'].set_position(('axes', 1.2))
        self.lightax.set_frame_on(True)
        self.lightax.patch.set_visible(False)

        # Initalize plot lines with dummy data
        self.line1, = self.ax.plot(
            [x[0] for x in self.plotData], 'r--')  # Target Heat
        self.line2, = self.ax.plot(
            [x[1] for x in self.plotData], 'r-')  # Heat
        self.line3, = self.ax2.plot(
            [x[2] for x in self.plotData], 'b--')  # Target Cooling
        self.line4, = self.ax2.plot(
            [x[3] for x in self.plotData], 'b-')  # Cooling
        self.line5, = self.lightax.plot(
            [x[4] for x in self.plotData], 'k:')  # Light

        # Set parameter for the look of the figure
        self.ax.set_xlabel("Time")
        self.ax.set_ylim([0, 180])
        self.ax.set_ylabel(u"Heating-element in °C")
        self.ax.yaxis.label.set_color("red")
        self.ax.tick_params(axis="y", colors="red")
        self.ax2.set_ylim([0, 30])
        self.ax2.set_ylabel(u"Cooling-element in °C")
        self.ax2.yaxis.label.set_color("blue")
        self.ax2.tick_params(axis="y", colors="blue")
        self.lightax.set_ylim([0, 1])
        self.lightax.set_ylabel(u"LED-Brightness")
        self.lightax.yaxis.label.set_color("black")
        self.lightax.tick_params(axis="y", colors="black")

        # Show figure in tkinter widget
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid()
        self.canvas._tkcanvas.grid(column=2, row=1, rowspan=100, sticky=W + S)


    def updatePlot(self):
        if self.sublimator.running:
            self.progend = False
            self.ax.set_title("")
            data = self.sublimator.datalog[:]
            if self.sublimator.progindex == 0:

                self.seplist[self.sublimator.progindex].configure(disabledbackground="cyan")

            else:
                self.seplist[self.sublimator.progindex].configure(disabledbackground="cyan")
                self.seplist[self.sublimator.progindex - 1].configure(disabledbackground="white")

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

            self.line5.set_xdata(np.arange(len(self.plotData)))
            self.line5.set_ydata([x[4] for x in self.plotData])


            # self.ax.plot()
            # self.ax2.plot()
            self.fig.canvas.draw()

        self.after(1000, self.updatePlot)

        if not self.sublimator.running:
            if self.progend is False and self.checkvariable.get() is 1:
                # Kompletter Plot wird am Ende gezeichnet wenn Checkbox aktiv
                self.saveEndPlot()

                self.progend = True

            for sep in self.seplist:
                sep.configure(disabledbackground="white")

            self.startButton.config(text="Start")
            self.saveCheckbox.configure(state="normal")

    def saveEndPlot(self):
        name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "_" + self.sequences[
            self.runner].name
        figurefile = "./figs/" + name + ".png"
        self.ax.lines.pop(0)
        self.ax2.lines.pop(0)
        self.lightax.pop(0)


        self.line1, = self.ax.plot(
            [x[0] for x in self.sublimator.datalog], 'r--')  # Target Heat
        self.line2, = self.ax.plot(
            [x[1] for x in self.sublimator.datalog], 'r-')  # Heat
        self.line3, = self.ax2.plot(
            [x[2] for x in self.sublimator.datalog], 'b--')  # Target Cooling
        self.line4, = self.ax2.plot(
            [x[3] for x in self.sublimator.datalog], 'b-')  # Cooling
        self.line5, = self.lightax.plot(
            [x[4] for x in self.sublimator.datalog], 'k:')  # Light

        # self.line1.set_xdata(np.arange(len(self.sublimator.datalog)))
        # self.line1.set_ydata([x[0] for x in self.sublimator.datalog])
        # self.line2.set_xdata(np.arange(len(self.sublimator.datalog)))
        # self.line2.set_ydata([x[1] for x in self.sublimator.datalog])
        # self.line3.set_xdata(np.arange(len(self.sublimator.datalog)))
        # self.line3.set_ydata([x[2] for x in self.sublimator.datalog])
        # self.line4.set_xdata(np.arange(len(self.sublimator.datalog)))
        # self.line4.set_ydata([x[3] for x in self.sublimator.datalog])
        # self.line5.set_xdata(np.arange(len(self.sublimator.datalog)))
        # self.line5.set_ydata([x[4] for x in self.sublimator.datalog])

        self.ax.set_title(name)
        self.fig.savefig(figurefile)
        self.sublimator.logger.info(
            "Figure with collected data was created: {}".format(figurefile))
        self.showDiagram()

    def updateConsole(self):
            '''
            Updatet die Konsolenausgabe.
            Verhindert Probleme mit Multithrading und Tkinter...
            '''

            self.newlen = len(self.sublimator.log_capture_string.getvalue())
            # Update der Konsole wenn neue Daten vorliegen
            if 0 < self.newlen != self.oldlen:
                self.oldlen = self.newlen
                # Inhalt komplett loeschen
                self.textField.configure(state=NORMAL)
                self.textField.delete(1.0, END)
                self.log = self.sublimator.log_capture_string.getvalue()
                # Neuen Inhalt einfuegen
                self.textField.insert(END, self.log)
                self.textField.configure(state=DISABLED)
                self.textField.yview(END)  # Setzt Scrollbar ans Ende
            # Update nach einer Sekunde, ruft Methode neu auf
            self.after(1000, self.updateConsole)


def _quit():
    '''
    Sorgt dafür das alle Threads in Tkinter und matplotlib richtig geschlossen werden
    :return:
    '''
    root.quit()
    root.destroy()


if __name__ == '__main__':
    sublimator = Sublimator.Sublimator()
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", _quit)
    myapp = Gui(sublimator, master=root)

    myapp.master.title("Sublimator")
    myapp.master.minsize(860, 560)
    myapp.after(300, myapp.updatePlot)
    myapp.after(1000, myapp.updateConsole)
    myapp.mainloop()
