from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QIcon
import sys, os, json, time
from modules.radio.radio import *
path=os.path.dirname(os.path.abspath( __file__ )).rsplit('/', 1)
form_class = uic.loadUiType(path[0]+"/"+path[1]+"/Si7403.ui")[0]


class radio(QtWidgets.QMainWindow, form_class):

    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.control=control(self)
        self.focused=False
        
        
    def loaded(self):
        # setup buttons
        for number in range(1,6):
            button = getattr(self, "btn_Station"+str(number))
            button.clicked.connect(lambda: self.channel())
        self.btn_Seekup.clicked.connect(lambda: self.control.seekUp())
        self.btn_Seekdown.clicked.connect(lambda: self.control.seekDown())
        self.btn_Tuneup.clicked.connect(lambda: self.control.tuneUp())
        self.btn_Tunedown.clicked.connect(lambda: self.control.tuneDown())

    def focus(self):
        self.focused=True
        self.parent.setInfo("Radio", self.settings["Si4703"]["currentStation"]+" MHz")
        self.setChanel(self.settings["Si4703"]["currentStation"])
        
    def pause(self):
        self.focused=False
        self.control.setVolume(0)
    
    def stop(self):
        self.pause()
        
    def play(self):
        self.control.setVolume(15)

    def channel(self):
        button=self.sender()
        index=button.objectName().replace("btn_Station","")
        frequenz=self.settings["Si4703"]["stations"][str(index)]
        self.setChanel(frequenz)
                 
    def setChanel(self, freq):
        self.settings["Si4703"]["currentStation"]=freq
        self.control.setChannel(float(freq)*10)
        self.chanelButtons()
        #message = self.radioCommand("getStatus", "") #radio.getStatus();
        #print(message)

    def setControlInfo(self, info, value):
        if info=="frequence":
            value+=" MHz"
            self.lbl_Frequenz.setText(value)
            if self.focused:
                self.parent.setInfo("Radio", value)

    def chanelButtons(self):
        for number in range(1,6):
            button=getattr(self, "btn_Station"+str(number))
            css="background-image: url(./images/clear.gif);background-repeat: none; background-color: #eeeeee; border-radius: 5px; background-position: center; "
            if self.settings["Si4703"]["stations"][str(number)]!="":
                css+="border: 2px solid #e42659; "
            else:
                css+="border: 0px; "
            if self.settings["Si4703"]["currentStation"]==self.settings["Si4703"]["stations"][str(number)]:
                css+="color: #e42659;"
            else:
                css+="color: #000000;"
            button.setStyleSheet(css)

    def radioCommand(self, command, value):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", 2001))
            MESSAGE = '{"' + command + '" : "' + str(value) + '"}'
            #print("SEND :" + MESSAGE)
            s.send((MESSAGE).encode('utf-8'))
            data = s.recv(1024)
            s.close()
            return data.decode('utf-8').replace("'", '"')
        except:
            pass

