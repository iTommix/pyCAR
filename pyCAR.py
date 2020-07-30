#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
import sys, platform, os, importlib, alsaaudio, gpsd, datetime, json, time, signal
from xml.dom import minidom
from functools import partial
from subprocess import call
from system.mobile import *
#import system.volume as volume
import system.pulsecontroller as pulsecontroller
from system.QTWidgets import *
#import system.dialog as dialog

sys.modules["QTWidgets"]=QTWidgets
path=os.path.dirname(os.path.abspath( __file__ ))
form_class = uic.loadUiType("./system/gui.ui")[0]

class pyCAR(QtGui.QMainWindow, form_class):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.frame.installEventFilter(self)
        self.modules={}
        self.pages = []
        self.setup = minidom.parse('./system/config.xml')

        self.modules["pyCAR"]={}
        self.modules["pyCAR"]["deck"]=0
        self.modules["pyCAR"]["instance"]=self
        #self.volume = volume
        #self.volume.parent = self
        
        self.pa = pulsecontroller.Pulsecontroller(self)
        
        
        self.player = None
        self.active = None
        self.mobile=mobile()
        self.mobile.parent = self
        gpsd.connect()
        self.volumeViewSetup()
        self.readConfig()
        self.home.setStyleSheet("background-color: #bbb;")
        
        self.btnVolumeUp.clicked.connect(lambda: self.volumeUp())
        self.btnVolumeDown.clicked.connect(lambda: self.volumeDown())
        self.btnMute.clicked.connect(lambda: self.pa.mute())
        self.btnHome.clicked.connect(lambda: self.switchModule(0))
        
        self.btnSATstatus.clicked.connect(lambda: self.showMessage("Titel", "Message", progress=100))

        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.timefunctions())
        self.timer.start(1000)

    def closeEvent(self, event):
        if self.modules.get("navit"):
            os.kill(self.modules["navit"]["instance"].pid, signal.SIGINT)
        self.saveConfig()
        event.accept()

    def eventFilter(self, source, event):
        #print(source, event, event.type())
        return QtGui.QWidget.eventFilter(self, source, event)
    
    def resume(self):
        if self.player != None :
            self.mainFrame.setCurrentIndex(self.modules[self.player]["deck"])
            if self.modules[self.player]["instance"] != self :
                self.active = self.player
                self.volume.setVolume(self.modules[self.player]["instance"].settings["volume"])
                self.modules[self.player]["instance"].play()
        else:
            self.mainFrame.setCurrentIndex(0)
            
    def stopPlayer(self):
        if self.player != None and hasattr(self.modules[self.player]["instance"], 'stop'):
            self.modules[self.player]["instance"].stop()

    def switchModule(self, deck):
        self.mainFrame.setCurrentIndex(deck)
        for module in self.modules:
            if self.modules[module]["instance"] != self and self.modules[module]["instance"].stack.currentIndex() > 0:
                self.modules[module]["instance"].stack.setCurrentIndex(0)
            self.pages = [0]
            if deck==self.modules[module]["deck"]:
                self.active = module
                if hasattr(self.modules[module]["instance"], 'focus'):
                    self.modules[module]["instance"].focus()
                if hasattr(self.modules[module]["instance"], 'play') and module != self.player:
                    if self.player != None:
                        self.modules["setup"]["instance"].equalizer.save_profile(self.player)
                        #self.volume.setVolume(0, False)
                        self.modules[self.player]["instance"].stop()
                        time.sleep(0.3)
                    self.player = module
                    self.modules["setup"]["instance"].equalizer.load_profile(self.player)
                    #self.volume.setVolume(self.modules[self.player]["instance"].settings["volume"])
                    self.modules[module]["instance"].play()
                
                    
    def setInfo(self, artist, title):
        self.lbl_Artist.setText(artist)
        self.lbl_Title.setText(title)
        
    def getSongLength(self, value):
        m, s = divmod(value, 60)
        return "%02d:%02d" % (m, s)
    
    def pageBack(self, stack):
        print(stack.whatsThis())
        print("back from", self.pages[-1], "to", self.pages[-2])
        if stack.currentIndex()>0:
            stack.setCurrentIndex(self.pages[-2])
            self.pages.pop()
            
    def setPage(self, stack, page):
        print(stack.whatsThis())
        print("from", stack.currentIndex(), "to", page)
        if page > 0:
            self.pages.append(page)
        else:
            self.pages = [0]
        stack.setCurrentIndex(page)
        print(self.pages)
    
    def volumeUp(self):
        try:
            v=self.modules[self.active]["instance"].settings["volume"]["value"]
            m=self.active
        except:
            try:
                v=self.modules[self.player]["instance"].settings["volume"]["value"]
                m=self.player
            except:
                pass
        try:
            if v<100:
                self.volumeViewTimer.start(2000)
                v=v+1
                self.modules[m]["instance"].settings["volume"]["value"]=v
                #if hasattr(self.modules[m]["instance"], 'play') or (m=="phone" and self.modules["phone"]["instance"].call==1):
                self.pa.setVolume(m)
                self.showVolumeView(v, m)
        except:
            pass
    
    def volumeDown(self):
        try:
            v=self.modules[self.active]["instance"].settings["volume"]["value"]
            m=self.active
        except:
            try:
                v=self.modules[self.player]["instance"].settings["volume"]["value"]
                m=self.player
            except:
                pass
        try:
            if v>0:
                self.volumeViewTimer.start(2000)
                v=v-1
                self.modules[m]["instance"].settings["volume"]["value"]=v
                print(m)
                #if hasattr(self.modules[m]["instance"], 'play') or (m=="phone" and self.modules["phone"]["instance"].call==1):

                self.pa.setVolume(m)
                if v==0 and hasattr(self.modules[m]["instance"], 'pause'):
                    self.modules[m]["instance"].pause()
                self.showVolumeView(v, m)
        except:
            pass

########################################################################
##
## Section Volume-Functions
##
########################################################################

    def showVolumeView(self, volume, module):
        self.volumeView.show()
        self.volumeSlider.setValue(volume)
        self.volumeLabel.setText(self.modules[module]["name"])
        
    def hideVolumeView(self):
        self.volumeView.hide()
        self.volumeViewTimer.stop()

    def volumeViewSetup(self):
        font = QtGui.QFont('SansSerif', 15, QtGui.QFont.Bold)
        self.volumeView = QtGui.QWidget(self)
        self.volumeView.setGeometry(QtCore.QRect(290, 120, 320, 180))
        self.volumeView.setObjectName("volumeView")
        self.volumeView.setStyleSheet("background-image: url(./images/volumeViewBG.png); border-radius: 10px;")
        
        self.volumeLabel=QtGui.QLabel(self.volumeView)
        self.volumeLabel.setGeometry(QtCore.QRect(0, 0, 320, 40))
        self.volumeLabel.setStyleSheet("color: #fff; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0;border-bottom-left-radius: 0;background-image: none; background-color: #000")
        self.volumeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.volumeLabel.setFont(font)       
        
        self.volumeSlider = QtGui.QProgressBar(self.volumeView)
        self.volumeSlider.setGeometry(QtCore.QRect(10, 80, 300, 22))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(30)
        self.volumeSlider.setStyleSheet("border-width: 0px; background: transparent;color: #edc87e; font-weight: bold; text-align: center; background-color: #aaaaaa")
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        self.volumeView.hide()
        self.volumeViewTimer = QtCore.QTimer()
        self.volumeViewTimer.timeout.connect(self.hideVolumeView)


        self.dialogView = QtGui.QWidget(self)
        self.dialogView.setGeometry(QtCore.QRect(290, 120, 320, 180))
        self.dialogView.setObjectName("dialogView")
        self.dialogView.setStyleSheet("background-image: url(./images/volumeViewBG.png); border-radius: 10px;")
        self.dialogView.hide()
        
        self.dialogTitle=QtGui.QLabel(self.dialogView)
        #self.dialogTitle.setContentsMargins(0,5,0,5)
        self.dialogTitle.setGeometry(QtCore.QRect(0, 0, 320, 40))
        self.dialogTitle.setStyleSheet("color: #fff; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0;border-bottom-left-radius: 0;background-image: none; background-color: #000")
        self.dialogTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.dialogTitle.setFont(font)
        
        font = QtGui.QFont('SansSerif', 15)
        self.dialogMessage=QtGui.QLabel(self.dialogView)
        self.dialogMessage.setWordWrap(True)
        self.dialogMessage.setContentsMargins(5,5,5,5)
        self.dialogMessage.setGeometry(QtCore.QRect(0, 50, 320, 80))
        self.dialogMessage.setStyleSheet("color: #fff; border-top-left-radius: 0px; border-top-right-radius: 0px; border-bottom-right-radius: 0;border-bottom-left-radius: 0;background-image: none;")
        self.dialogMessage.setAlignment(QtCore.Qt.AlignLeft)
        self.dialogMessage.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.dialogMessage.setFont(font)
        self.dialogMessage.setVisible(False)
        
        self.dialogProgress = QtGui.QProgressBar(self.dialogView)
        self.dialogProgress.setGeometry(60, 135, 200, 20)
        self.dialogProgress.setVisible(False)

########################################################################
##
## 
##
########################################################################

    def showMessage(self, title, message, ok=False, progress=False, modal=True):
        self.dialogTitle.setText(title)
        if message != "":
            self.dialogMessage.setText(message)
            self.dialogMessage.setVisible(True)
        if progress != False:
            self.dialogProgress.setMaximum(progress)
            self.dialogProgress.setValue(0)
            self.dialogProgress.setVisible(True)
        self.dialogView.show()

        
    def closeMessage(self):
        self.dialogView.close()

########################################################################
##
## Read the Config and load the Modules
##
########################################################################

    def readConfig(self):
        row=1
        column=1
        startColumn=0
        count = len(self.modules)
        
        self.container.setParent(None)
        self.container = QtGui.QWidget(self.home)
        self.container.setGeometry(QtCore.QRect(0, 169, 700, 311))
        grid = QGridLayout(self.container)
        modules = self.setup.getElementsByTagName('module')
        
        for index, module in enumerate(self.sortModules(modules), start=1):
            if module != None:
                settings=json.loads(module.firstChild.data)
                if module.attributes["enabled"].value == "1":
                    # Import the Modules
                    if self.modules.get(module.attributes["name"].value):
                        button = self.getButton(module.attributes["name"].value, module.attributes["label"].value, self.modules[module.attributes["name"].value]["deck"])
                    else:
                        mod=importlib.import_module("modules."+module.attributes["name"].value+".module")
                        instance=getattr(mod, module.attributes["name"].value)(self, settings)
                        instance.parent = self
                        instance.settings = settings
                        try:
                            uic.loadUi("./modules/"+module.attributes["name"].value+"/gui.ui", instance)
                        except:
                            pass
                        pages = int(module.attributes["pages"].value)
                        stack = QTWidgets().StackedWidget()
                        stack.setWhatsThis(module.attributes["name"].value)
                        stack.setStyleSheet("background-image: url(./modules/"+module.attributes["name"].value+"/skin.png); border: 0px;")
                        for page in range(1, pages+1):
                            if page > 1:
                                backButton = QtGui.QToolButton(getattr(instance, "page"+str(page)))
                                backButton.setGeometry(QtCore.QRect(10, 10, 80, 50))
                                backButton.setStyleSheet("background-image: url(./images/close.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
                                backButton.clicked.connect(partial(getattr(self, 'pageBack'), stack)) 
                            stack.addWidget(getattr(instance, "page"+str(page)))
    
                        instance.stack = stack
                        layout = QtGui.QHBoxLayout()
                        layout.setContentsMargins(0, 0, 0, 0)
                        layout.addWidget(stack)
                        instance.centralwidget.setLayout(layout)
    
                        self.modules[module.attributes["name"].value]={}
                        self.modules[module.attributes["name"].value]["deck"]=count
                        self.modules[module.attributes["name"].value]["instance"]=instance
                        self.modules[module.attributes["name"].value]["name"] = module.attributes["label"].value
                        self.mainFrame.addWidget(instance)
                        
                        button = self.getButton(module.attributes["name"].value, module.attributes["label"].value, count)
                        count+=1
                        instance.loaded()
                        
                        
                    #####
                    grid.addWidget(button, row, startColumn+column)
                    if column>3:
                        column=1
                        row+=1
                        if row>2:
                            startColumn+=4
                            row=1
                    else:
                        column+=1
        #count-=1
        pa = self.setup.getElementsByTagName('pulseaudio')[0]
        self.pa.load(json.loads(pa.firstChild.data))
        
    def getButton(self, name, labelText, deck):
        font = QtGui.QFont()
        font.setBold(True)
        button = QWidget()
        button.setGeometry(QtCore.QRect(0, 0, 140, 110))

        # Add Image
        image = QtGui.QToolButton(button)
        image.setGeometry(QtCore.QRect(30, 0, 80, 80))
        image.setStyleSheet("background-image: url(./modules/"+name+"/button.png);background-repeat: none; border-radius: 10px; border: 0px;background-position: center")
        image.clicked.connect(partial(getattr(self, 'switchModule'), deck))
            
        # Add Label
        label=QtGui.QLabel(button)
        label.setGeometry(QtCore.QRect(0, 90, 140, 20))
        label.setStyleSheet("color: #ffffff;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(font)
        label.setText(labelText)
        return button
        
    def sortModules(self, modules):
        sortedMods = [None] * len(modules)
        for module in modules:
            sortedMods[int(module.attributes["order"].value)]=module
        return sortedMods
        
    def saveConfig(self):
        modules = self.setup.getElementsByTagName('module')
        for module in modules:
            if module.attributes["enabled"].value == "1":
                try:
                    module.firstChild.data = json.dumps(self.modules[module.attributes["name"].value]["instance"].settings)
                except:
                    pass
        pa = self.setup.getElementsByTagName('pulseaudio')[0]
        pa.firstChild.data = json.dumps(self.pa.settings)
        with open("./system/config.xml", "w") as xml_file:
            self.setup.writexml(xml_file)
    
########################################################################
##
## Various Helper-Functions
##
########################################################################        

    def timefunctions(self):
        # Check Bluetooth-Status
        if self.mobile.getConnectedDevice():
            self.btnBTstatus.setStyleSheet("background-image: url(./images/bt_on.png);background-repeat: none; border: 0px;")
        else:
            self.btnBTstatus.setStyleSheet("background-image: url(./images/bt_off.png);background-repeat: none; border: 0px;")
        # Check GPS-Status
        packet = gpsd.get_current()
        style="background-image: url(./images/satellite.png);background-repeat: none; background-color: #ff0000; border: 0px;"
        if packet.sats>=20:
            style="background-image: url(./images/satellite.png);background-repeat: none; background-color: #00ff00; border: 0px;"
        if packet.sats>=10:
            style="background-image: url(./images/satellite.png);background-repeat: none; background-color: #fcdc5c; border: 0px;"
        self.btnSATstatus.setStyleSheet(style)
        # Set Time
        self.lblTime.setText('{0:%H:%M}'.format(datetime.datetime.now()))
        






def main():
    app = QtGui.QApplication(sys.argv)
    screen = app.desktop().screenGeometry()
    form = pyCAR()
    if screen.width()==800 and screen.height()==480:
        form.showFullScreen()
    else:
        form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()