from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QIcon, QImage, QPixmap
import mplayer, sys, os, json, time
from xml.dom import minidom
from urllib.request import Request, urlopen

path=os.path.dirname(os.path.abspath( __file__ )).rsplit('/', 1)
form_class = uic.loadUiType(path[0]+"/"+path[1]+"/internet.ui")[0]

player = mplayer.Player()

class radio(QtGui.QMainWindow, form_class):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent=parent
        self.stations={}
        self.setupUi(self)
        self.stationList.itemClicked.connect(lambda: self.setChannel(self.stationList.currentRow()))
        self.settings=settings
        self.readChannels()
        
        
        
    def focus(self):
        pass
                    
    def pause(self):
        if not player.paused:
            player.pause()
    
    def stop(self):
        self.pause()
    
    def play(self):
        self.setChannel(self.settings["internet"]["currentStation"])            
            
    def pullInfo(self):
        self.parent.lbl_Artist.setText("")
        self.parent.lbl_Title.setText(self.lbl_Text.text())
        
    def setChannel(self, item):
        station=self.stations[item]
        self.lbl_Text.setText(station["name"])
        player.loadfile(station["url"])
        self.settings["internet"]["currentStation"]=item
        self.pullInfo()
    
    def readChannels(self):
        i=0
        self.stationList.clear()
        self.stationList.clearSelection()
        path=os.path.realpath(__file__).rsplit('/', 2)
        dom = minidom.parse(self.settings["internet"]["path"]+"/stations.xml")
        items = dom.getElementsByTagName('item')
        for item in items:
            self.stations[i]={}
            self.stations[i]["name"]=item.attributes["name"].value
            self.stations[i]["url"]=item.attributes["url"].value
            itm = QtGui.QListWidgetItem(item.attributes["name"].value);
            image=path[0]+'/'+path[1]+'/radio.png'
            if item.attributes["image"].value:
                req = Request(item.attributes["image"].value, headers={'User-Agent': 'Mozilla/5.0'})
                artwork = urlopen(req).read()
                new = QImage()
                new.loadFromData(artwork)
                image = QPixmap(new).scaledToHeight(150, QtCore.Qt.SmoothTransformation)
            
            itm.setIcon(QIcon(image));
            self.stationList.addItem(itm);
            i=i+1
            self.stationList.setCurrentRow(self.settings["internet"]["currentStation"])
