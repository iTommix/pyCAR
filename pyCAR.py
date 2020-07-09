#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
import sys, platform, os, importlib, alsaaudio, gpsd, datetime, json, time, schedule
from xml.dom import minidom
from functools import partial
from subprocess import call
from system.mobile import *
import system.volume as volume
from system.QTWidgets import *

sys.modules["QTWidgets"]=QTWidgets
path=os.path.dirname(os.path.abspath( __file__ ))
form_class = uic.loadUiType("./system/gui.ui")[0]


class pyCAR(QtGui.QMainWindow, form_class):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.schedule = schedule
        self.frame.installEventFilter(self)
        self.modules={}
        self.fakeModules={}
        self.tasks=[]
        self.modules["pyCAR"]={}
        self.modules["pyCAR"]["deck"]=0
        self.modules["pyCAR"]["instance"]=self
        self.volume = volume
        self.volume.parent = self
        self.player = None
        self.active = None
        self.mobile=mobile()
        self.mobile.parent = self
        gpsd.connect()
        self.volumeViewSetup()
        self.readConfig()
        self.home.setStyleSheet("background-color: #000000;")
        
        self.btnVolumeUp.clicked.connect(lambda: self.volumeUp())
        self.btnVolumeDown.clicked.connect(lambda: self.volumeDown())
        self.btnMute.clicked.connect(lambda: self.volume.mute())
        self.btnHome.clicked.connect(lambda: self.switchModule(0))
        
        self.timer = QtCore.QTimer()
        #self.timer.timeout.connect(lambda: self.timefunctions())
        self.timer.timeout.connect(lambda: self.schedule.run_pending())
        self.timer.start(1000)
        
        self.schedule.every().second.do(self.timefunctions).tag("primary")

    def closeEvent(self, event):
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
            if deck==self.modules[module]["deck"]:
                self.active = module
                if hasattr(self.modules[module]["instance"], 'focus'):
                    self.modules[module]["instance"].focus()
                if hasattr(self.modules[module]["instance"], 'play') and module != self.player:
                    if self.player != None:
                        self.volume.setVolume(0, False)
                        self.modules[self.player]["instance"].stop()
                        time.sleep(0.3)
                    self.player = module
                    self.volume.setVolume(self.modules[self.player]["instance"].settings["volume"])
                    self.modules[module]["instance"].play()
                
                    
    def setInfo(self, artist, title):
        self.lbl_Artist.setText(artist)
        self.lbl_Title.setText(title)
        
    def getSongLength(self, value):
        m, s = divmod(value, 60)
        return "%02d:%02d" % (m, s)
    
    def volumeUp(self):
        try:
            v=self.modules[self.active]["instance"].settings["volume"]
            m=self.active
        except:
            v=self.modules[self.player]["instance"].settings["volume"]
            m=self.player
        if v<100:
            v=v+1
            self.modules[m]["instance"].settings["volume"]=v
            if hasattr(self.modules[m]["instance"], 'play') or (m=="phone" and self.modules["phone"]["instance"].call==1):
                self.volume.setVolume(self.modules[m]["instance"].settings["volume"])
            self.showVolumeView(v, m)
    
    def volumeDown(self):
        try:
            v=self.modules[self.active]["instance"].settings["volume"]
            m=self.active
        except:
            v=self.modules[self.player]["instance"].settings["volume"]
            m=self.player
        if v>0:
            v=v-1
            self.modules[m]["instance"].settings["volume"]=v
            print(m)
            if hasattr(self.modules[m]["instance"], 'play') or (m=="phone" and self.modules["phone"]["instance"].call==1):
                self.volume.setVolume(self.modules[m]["instance"].settings["volume"])
            if v==0 and hasattr(self.modules[m]["instance"], 'pause'):
                self.modules[m]["instance"].pause()
            self.showVolumeView(v, m)

########################################################################
##
## Section Volume-Functions
##
########################################################################

    def showVolumeView(self, volume, module):
        self.volumeView.show()
        self.schedule.every(3).seconds.do(self.hideVolumeView).tag("hideVolumeView")
        self.volumeSlider.setValue(volume)
        self.volumeLabel.setText(self.modules[module]["name"])

    def showVolumeView_old(self, volume, module):
        self.volumeView.show()
        self.schedule.every(2).seconds.do(self.hideVolumeView).tag("hideVolumeView")
        self.volumeSlider.setValue(volume)
        if self.player != None:
            self.volumeLabel.setText(self.modules[self.active]["name"])
            if self.mainFrame.currentIndex()>0:
                #print("Player is:", self.player," Set Volume to ", self.modules[self.player]["instance"].settings["volume"])
                self.modules[self.player]["instance"].settings["volume"] = volume
        
    def hideVolumeView(self):
        self.volumeView.hide()
        self.schedule.clear('hideVolumeView')

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

########################################################################
##
## Read the Config and load the Modules
##
########################################################################

    def readConfig(self):
        font = QtGui.QFont()
        font.setBold(True)
        y=120
        x=0
        count=1
        dom = minidom.parse('./system/config.xml')
        # Import Mainsettings
        # settings=dom.getElementsByTagName('settings')[0]
        # self.settings=json.loads(settings.firstChild.data)
        # Collect all Modules
        modules = dom.getElementsByTagName('module')
        for module in self.sortModules(modules):
            if module != None:
                settings={}
                try:
                    settings=json.loads(module.firstChild.data)
                except:
                    pass
                if module.attributes["enabled"].value == "1":
                    # Import the Modules            
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
                    stack.setStyleSheet("background-image: url(./modules/"+module.attributes["name"].value+"/skin.png); border: 0px;")
                    for page in range(1, pages+1):
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
                    self.modules[module.attributes["name"].value]["order"] = module.attributes["order"].value
                    self.modules[module.attributes["name"].value]["pages"] = module.attributes["pages"].value
                    #self.modules[count-1]=module.attributes["name"].value
                    #instance.frame.setStyleSheet("background-image: url(./modules/"+module.attributes["name"].value+"/skin.png); border: 0px;")
                    self.mainFrame.addWidget(instance)
        
                    # Add Button to Homescreen
                    button = QtGui.QToolButton(self.home)
                    button.setObjectName(module.attributes["name"].value)
                    button.setGeometry(QtCore.QRect(65+(x*164), y, 80, 80))
                    button.setStyleSheet("background-image: url(./modules/"+module.attributes["name"].value+"/button.png);background-repeat: none; border-radius: 10px; border: 0px;background-position: center")
                    button.clicked.connect(partial(getattr(self, 'switchModule'), count))
                        
                    # Add Label
                    label=QtGui.QLabel(self.home)
                    label.setGeometry(QtCore.QRect(35+(x*164), y+90, 140, 20))
                    label.setStyleSheet("color: #ffffff;")
                    label.setAlignment(QtCore.Qt.AlignCenter)
                    label.setFont(font)
                    label.setText(module.attributes["label"].value)
                    instance.loaded()
                    count=count+1
                    if x>2:
                        x=0
                        y=y+170
                    else:
                        x=x+1
                else:
                    self.fakeModules[module.attributes["name"].value]={}
                    self.fakeModules[module.attributes["name"].value]["instance"] = None
                    self.fakeModules[module.attributes["name"].value]["name"] = module.attributes["label"].value
                    self.fakeModules[module.attributes["name"].value]["order"] = module.attributes["order"].value
                    self.fakeModules[module.attributes["name"].value]["pages"] = module.attributes["pages"].value
                    self.fakeModules[module.attributes["name"].value]["settings"]=settings
        vol = dom.getElementsByTagName('volume')[0]
        volume.init(json.loads(vol.firstChild.data), self.modules["setup"]["instance"].settings["mixer"])

        
    def sortModules(self, modules):
        sortedMods = [None] * len(modules)
        for module in modules:
            sortedMods[int(module.attributes["order"].value)]=module
        return sortedMods
        
    def saveConfig(self):
        config = '<?xml version="1.0" encoding="UTF-8" ?>\n'
        config+= '<pyCAR>\n'
        config+= '  <modules>\n'
        modules={}
        modules.update(self.modules)
        modules.update(self.fakeModules)
        for module in modules:
            if module != "pyCAR":
                try:
                    settings = json.dumps(self.modules[module]["instance"].settings)
                except:
                    settings = json.dumps(modules[module]["settings"])
                config+='       <module name="'+module+'" label="'+modules[module]["name"]+'" enabled="'+("0" if modules[module]["instance"] == None else "1")+'" order="'+modules[module]["order"]+'" pages="'+modules[module]["pages"]+'">'+settings+'</module>\n'
        config+= '  </modules>\n'
        config+= '  <volume>{"mute":0,"balance":0,"volume":30}</volume>\n'
        config+= '</pyCAR>\n'
        file = open('./system/config.xml', "w")
        file.write(config)
        
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
        if packet.sats>20:
            style="background-image: url(./images/satellite.png);background-repeat: none; background-color: #00ff00; border: 0px;"
        if packet.sats>10:
            style="background-image: url(./images/satellite.png);background-repeat: none; background-color: #fcdc5c; border: 0px;"
        self.btnSATstatus.setStyleSheet(style)
        # Set Time
        self.lblTime.setText('{0:%H:%M}'.format(datetime.datetime.now()))
        






def main():
    app = QtGui.QApplication(sys.argv)
    form = pyCAR()
    if len(sys.argv)>1:
        if sys.argv[1]=="fullscreen":
            form.showFullScreen()
    else:
        form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()