#dependancies
import pip
import argparse

def import_or_install(package):
    try:
        return __import__(package)
    except ImportError:
        pip.main(['install', package])

time = import_or_install('time')
os   = import_or_install('os')
sys  = import_or_install('sys')
serial = import_or_install('serial')
from serial import Serial
threading = import_or_install('threading')
from datetime import datetime
from PyQt5.QtWidgets import *
import random
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np



class Plt(FigureCanvas):

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super(Plt, self).__init__(self.fig)
        self.setParent(parent)
        # self.axes2.spines['bottom'].set_color('orange')
        # self.axes2.tick_params(axis='x', colors='orange')
        # self.axes2.xaxis.label.set_color('orange')




class pumpObj():

    def __init__(self,app,ID,name,state,flow,calCoef,xPos,yPos):
        self.ID      = ID
        self.name    = name
        self.state   = state
        self.flow    = flow
        self.calCoef = calCoef

        self.control = controlObj(app,self,xPos,yPos,16)
        #self.control.button.setStyleSheet("background-color:rgb(0,255,0)")

    def setSpeed(self,flow):
        cmd = self.flow*self.calCoef
        print(self.ID+cmd)

    def changeState(self):
        self.state = not self.state
        print(self.name+' '+'state changed to ' + str(self.state))


class controlObj():
    
    def __init__(self,app,pump,x,y,FS):
        
        #BUTTON#####
        self.button = QPushButton(pump.name,app)
        self.button.move(x, y)
        self.button.resize(175,80)
        font=self.button.font()
        font.setPointSize(FS)
        self.button.setFont(font)
        self.button.setCheckable(True)
        self.button.setStyleSheet("background-color:rgb(255,0,0)")
        self.button.clicked.connect(lambda: app.clicked(pump))
        #TEXTBOX#####
        self.textbox = QLineEdit(app)
        self.textbox.move(x+185,y)
        self.textbox.resize(100,80)
        font=self.textbox.font()
        font.setPointSize(FS)
        self.textbox.setFont(font)
        self.textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox.setText(str(pump.flow))
        self.textbox.returnPressed.connect(lambda: app.flowChg(pump))
        #LABEL#####
        self.label = QLabel("[mL/min]",app)
        self.label.move(x+205,y-40)
        self.label.resize(150,40)
        font=self.label.font()
        font.setPointSize(FS-6)
        self.label.setFont(font)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Serial Object############################################################################
        self.DISCO = serial.Serial('COM6',9600)
        self.DISCO.flushInput()
        self.DISCO.write(('R').encode())
        ##########################################################################################

        self.setStyleSheet("background-color: white;") 

        #DATA FILE#####
        path = os.path.join(os.getcwd(),'DISCO_III_DATA')
        
        if not os.path.exists(path):
            os.makedirs(path)

        filename=datetime.now().strftime('%Y%m%dT%H%M%S') + '_data.txt'
        
        self.dataFile = os.path.join(path,filename)
        with open(self.dataFile,'a') as trgt:
            trgt.write('Time,Tout,Fout,Tin,Fin,PMT,sampleFlow,mclaFlow,sodFlow,EventFlag\n')

        filename=datetime.now().strftime('%Y%m%dT%H%M%S') + '_notes.txt'
        
        self.noteFile = os.path.join(path,filename)
        
        

        #PLOT initilization#######################################################################
        self.plt1 = Plt(self,width=24, height=12, dpi=100)
        self.plt1.move(-100,50)
        self.plt1.axes.set_ylabel('PMT Counts', weight='bold', color='red')
        self.plt1.axes.set_xlabel('Time',weight='bold')
        self.plt1.axes.set_title('Time,PMT Counts',weight='bold',fontsize=40)
        self.line, = self.plt1.axes.plot(datetime.now(),0,'.-r')
        #self.plt1.axes.spines['left'].set_color('red')
        #self.plt1.axes.tick_params(axis='y', color='red')
        #self._plot_ref = self.line[0]
        self.plt1.draw()
        self.xData = []
        self.pData = []
        ##########################################################################################

        #Control Objects##########################################################################
        #Pumps....
        x=150
        inc=350
        self.samplePump = pumpObj(self,ID='c',name='Sample',state=False,flow=7,calCoef=123.785,xPos=x,yPos=60)
        self.mclaPump   = pumpObj(self,ID='b',name='MCLA',state=False,flow=7,calCoef=123.785,xPos=x+inc,yPos=60)
        self.sodPump    = pumpObj(self,ID='d',name='SOD',state=False,flow=1,calCoef=123.785,xPos=x+2*inc,yPos=60)
        self.sotsPump   = pumpObj(self,ID='d',name='SOTs',state=False,flow=2,calCoef=123.785,xPos=x+3*inc,yPos=60)

        self.sotsPump.control.button.clicked.connect(lambda: self.actionSOTs(self.sotsPump))
        self.sotsPump.control.textbox.setVisible(False)
        self.sotsPump.control.label.setVisible(False)

        #write cal coef used to notes file
        with open(self.noteFile,'a') as trgt:
                trgt.write(filename+'\n\n')
                trgt.write('calibration coef. for Sample pump: '+str(self.samplePump.calCoef)+'[mL/counts]\n')
                trgt.write('calibration coef. for MCLA pump: '+str(self.mclaPump.calCoef)+'[mL/counts]\n')
                trgt.write('calibration coef. for SOD pump: '+str(self.sodPump.calCoef)+'[mL/counts]\n\n')

        #Event Button....
        self.eventBut   = QPushButton('Event 1',self)
        self.eventBut.num = 1
        self.eventBut.Flag = False
        self.eventBut.move(1600, 60)
        self.eventBut.resize(175,80)
        font=self.eventBut.font()
        font.setPointSize(16)
        self.eventBut.setFont(font)
        self.eventBut.setStyleSheet("background-color:rgb(0,255,0)")
        self.eventBut.clicked.connect(self.note)
        #notes checkbox....
        self.noteBox = QCheckBox("Note",self)
        self.noteBox.move(1800,65)
        self.noteBox.resize(160,70)
        self.noteBox.setStyleSheet("QCheckBox::indicator { width: 60px; height: 60px;}")
        font=self.noteBox.font()
        font.setPointSize(12)
        self.noteBox.setFont(font)
        ##########################################################################################

        #Numeric Inputs###########################################################################
        #axis scalers###################################################
        xRef = 900
        self.xScale = QDoubleSpinBox(self)
        self.xScale.move(xRef,1185)
        self.xScale.resize(150,80)
        font=self.xScale.font()
        font.setPointSize(12)
        self.xScale.setFont(font)
        self.xScale.setAlignment(QtCore.Qt.AlignCenter)        
        self.xScale.setDecimals(0)
        self.xScale.setMaximum(5*60*2) #5mins at 2Hz in seconds
        self.xScale.setValue(120)
        self.xScale.setSingleStep(60)
        #self.xScale.setMaximum
        self.xScale.setMinimum(60)
        ####axis scaler label
        self.xScaleLabel = QLabel('X-AXIS:',self)
        self.xScaleLabel.move(xRef-100, 1200)
        self.xScaleLabel.resize(60,50)
        font=self.xScaleLabel.font()
        font.setPointSize(12)
        self.xScaleLabel.setFont(font)
        #################################################################
        #PMT Voltage#####################################################
        self.pmtVoltage = QDoubleSpinBox(self)
        self.pmtVoltage.move(xRef+300,1185)
        self.pmtVoltage.resize(150,80)
        font=self.pmtVoltage.font()
        font.setPointSize(12)
        self.pmtVoltage.setFont(font)
        self.pmtVoltage.setAlignment(QtCore.Qt.AlignCenter)        
        self.pmtVoltage.setDecimals(0)
        self.pmtVoltage.setMaximum(1200) #5mins at 2Hz in seconds
        self.pmtVoltage.setValue(1200)
        self.pmtVoltage.setSingleStep(100)
        #self.xScale.setMaximum
        self.pmtVoltage.setMinimum(100)
        self.pmtVoltage.valueChanged.connect(lambda: self.pmtVoltChg())    
        ####axis scaler label
        self.pmtVoltageLabel = QLabel('PMT V:',self)
        self.pmtVoltageLabel.move(xRef+200, 1200)
        self.pmtVoltageLabel.resize(60,50)
        font=self.pmtVoltageLabel.font()
        font.setPointSize(12)
        self.pmtVoltageLabel.setFont(font)
        #################################################################
        #PMT Integration#################################################
        self.pmtIT = QDoubleSpinBox(self)
        self.pmtIT.move(xRef+600,1185)
        self.pmtIT.resize(150,80)
        font=self.pmtIT.font()
        font.setPointSize(12)
        self.pmtIT.setFont(font)
        self.pmtIT.setAlignment(QtCore.Qt.AlignCenter)        
        self.pmtIT.setDecimals(0)
        self.pmtIT.setMaximum(1000) #5mins at 2Hz in seconds
        self.pmtIT.setValue(10)
        self.pmtIT.setSingleStep(10)
        #self.xScale.setMaximum
        self.pmtIT.setMinimum(10)
        self.pmtIT.valueChanged.connect(lambda: self.pmtITChg())   
        ####axis scaler label
        self.pmtITLabel = QLabel('PMT IT:',self)
        self.pmtITLabel.move(xRef+500, 1200)
        self.pmtITLabel.resize(60,50)
        font=self.pmtITLabel.font()
        font.setPointSize(12)
        self.pmtITLabel.setFont(font)
        ##########################################################################################
        
        #Data Labels##############################################################################
        #filename label....
        self.fileLabel = QLabel('LOGGING TO: '+filename,self)
        self.fileLabel.move(200, 1200)
        self.fileLabel.resize(450,50)
        font=self.fileLabel.font()
        font.setPointSize(12)
        self.fileLabel.setFont(font)
        ##########################################################################################
        
        #timer to redraw plot#####################################################################
        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(100)
        self.timer1.timeout.connect(self.update_plot)
        self.timer1.start()
        ##########################################################################################
        #x = threading.Thread(target=self.update_plot)
        #x.start()

        self.showMaximized()

        self.show()


    def pmtITChg(self):
        
        cmd = 'P'
        time = round(self.pmtIT.value()/10)
        cmd += str(time)
        
        self.DISCO.write(cmd.encode())

    def pmtVoltChg(self):
        
        cmd = 'V'
        voltage = round(self.pmtVoltage.value())
        cmd += str(voltage)

        self.DISCO.write(cmd.encode())

    
    def crtControl(self, pump, x, y, FS):

        #PUSH BUTTON#################################
        button = QPushButton(pump.name,self)
        button.move(x, y)
        button.resize(175,60)
        font=button.font()
        font.setPointSize(FS)
        button.setFont(font)
        button.setStyleSheet("background-color:rgb(153,153,153)")
        return button
        

    #button action
    def clicked(self,pump):
        pump.changeState()
        if pump.state:
            pump.control.button.setStyleSheet("background-color:rgb(0,255,0)")
            self.flowChg(pump)
        else:
            pump.control.button.setStyleSheet("background-color:rgb(255,0,0)")
            #print('pump off, cmd: ' + pump.ID +'2048')
            self.DISCO.write((pump.ID + '2048'+'\n').encode())
            self.DISCO.write((pump.ID + '2048'+'\n').encode())


    #flow rate changed 
    def flowChg(self,pump):
        pump.flow = float(pump.control.textbox.text())
        print('flowrate changed to ' + str(pump.flow) + ' [ml/min], cmd: ' + pump.ID + str(pump.flow*pump.calCoef+2048))
        if(pump.state):
            cmd = (pump.ID + str(pump.flow*pump.calCoef+2048)+'\n')
            self.DISCO.write(cmd.encode())
            self.DISCO.write(cmd.encode())
            print(cmd)

    #SOTs Button
    def actionSOTs(self,pump):
        self.sodPump.flow = pump.flow
        self.samplePump.flow = self.mclaPump.flow-self.sodPump.flow
        print(pump.flow)
        print(self.samplePump.flow)
        self.sodPump.control.textbox.setText(str(self.sodPump.flow))
        self.samplePump.control.textbox.setText(str(self.samplePump.flow))
        
        if(self.sotsPump.state):
            if(not self.samplePump.state):
                self.clicked(self.samplePump)
            if(not self.mclaPump.state):
                self.clicked(self.mclaPump)
            if(not self.sodPump.state):
                self.clicked(self.sodPump)
        else:   
            self.samplePump.control.textbox.setText('7') 
            self.flowChg(self.samplePump)
            self.mclaPump.control.textbox.setText('7') 
            self.flowChg(self.mclaPump)
            # self.clicked(self.samplePump)
            # self.clicked(self.mclaPump)
            self.clicked(self.sodPump)

    #event##
    def note(self):
        self.eventBut.Flag = True
        currentEventNum = str(self.eventBut.num)
        self.plt1.axes.axvline(datetime.now(),color = 'k')
        self.plt1.axes.text(datetime.now(),1,'E'+currentEventNum,weight='bold',fontsize=25)


        if(self.noteBox.isChecked()):
            text, ok = QInputDialog.getMultiLineText(self, self.eventBut.text()+' Input Dialog', 'Enter your note:')
            with open(self.noteFile,'a') as trgt:
                trgt.write('Event '+currentEventNum+'\n'+text+'\n\n')
        
        
            
        
        
        
    

    def update_plot(self):
        #print(self.DISCO.in_waiting)
        if(self.DISCO.in_waiting>0):
            print(self.DISCO.in_waiting)
            data = self.DISCO.readline().decode().replace('\r\n','').split(',') 
            t = datetime.now()
            #print(data)
            #print(self.DISCO.in_waiting)
            while(self.DISCO.in_waiting>0):
                self.DISCO.readline()
                #print('cleaning')

            if len(data) == 5:

                flows = str(self.samplePump.state*self.samplePump.flow)+','
                flows += str(self.mclaPump.state*self.mclaPump.flow)+','
                flows += str(self.sodPump.state*self.sodPump.flow)

                tString = t.strftime('%Y%m%dT%H%M%S')

                #file logging#################################################
                if(self.eventBut.Flag):
                    with open(self.dataFile,'a') as trgt:
                        trgt.write(tString+','+','.join(map(str,data))+','+flows+','+self.eventBut.text()+'\n')
                        self.eventBut.num+=1
                        self.eventBut.setText("Event " + str(self.eventBut.num))
                        self.eventBut.Flag=False
                else:
                    with open(self.dataFile,'a') as trgt:
                        trgt.write(tString+','+','.join(map(str,data))+','+flows+','+'\n')
                #file logging#################################################
                ##############################################################
                #local data storage###########################################
                #saves up to 5 minutes at 2 samples a second
                if len(self.pData) == 5*60*2:
                    self.xData = self.xData[1:] + [t]
                    self.pData = self.pData[1:] + [float(data[4])]
                    #self.tData =
                    #self.fData =
                else:
                    self.xData = self.xData + [t]
                    self.pData = self.pData + [float(data[4])]
                    #self.tData =
                    #self.fData =
                #local data storage###########################################
                ##############################################################
                #plot handling################################################
                dY = len(self.pData)            
                dT = int(self.xScale.value())
                
                if(dT>=dY):
                    xTemp=self.xData
                    pTemp=self.pData   
                else:
                    xTemp=self.xData[dY-dT:dY]
                    pTemp=self.pData[dY-dT:dY]

                self.line.set_data(xTemp,pTemp)

                self.plt1.axes.set_title(t.strftime('%H:%M:%S')+' , '+data[4],weight='bold',fontsize=30)
                M=max(pTemp);m=min(pTemp);diff=M-m
                #self.plt1.axes.set_ylim(m-(1/16)*diff,M+(1/16)*diff)
                self.plt1.axes.set_ylim(0,M+(1/16)*diff)
                self.plt1.axes.set_xlim(xTemp[0],xTemp[len(xTemp)-1])
                self.plt1.draw()

                # while not queue1.empty():
                #         queue1.get()
                # while queue1.empty():
                #     pass
                # data=queue1.get()
                # self.line.set_data(range(len(data)),data)
                
                # M=max(data);m=min(data);diff=M-m
                # self.plt1.axes.set_ylim(m-(1/16)*diff,max(data)+(1/16)*diff)
                self.plt1.draw()




if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.resize(2160,1440) 
     
    app.exec_()
    