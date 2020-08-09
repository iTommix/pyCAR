"""
from PyQt4 import Qt, QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import *
"""
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtCore

from types import *
import os, netifaces as ni, psutil, time, alsaaudio, pulsectl, importlib, sys
from glob import glob
from subprocess import call
from xml.dom import minidom
from dbus.mainloop.glib import DBusGMainLoop

path=os.path.dirname(os.path.abspath( __file__ ))

pulse = pulsectl.Pulse('pyCAR')
mod=importlib.import_module("modules.setup.equalizer")
DBusGMainLoop(set_as_default=True)


class tableModel(QtGui.QStandardItemModel):
    def __init__(self,datain,parent=None,*args):
        QtGui.QStandardItemModel.__init__(self,parent,*args)
        self.header = None
        self.modules = None
        #self.itemChanged.connect(self.itemChanged)
        
    def headerData(self,section,orientation,role=QtCore.Qt.DisplayRole):
        if orientation==QtCore.Qt.Vertical:
            if role==QtCore.Qt.DecorationRole:
                mPath = path.rsplit('/', 1)
                module = self.modules[section]
                return QtGui.QPixmap(mPath[0]+"/"+module.attributes["name"].value+"/button.png")
            if role==QtCore.Qt.DisplayRole:
                return ""
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Horizontal:
            return self.header[section]
        return QtGui.QStandardItemModel.headerData(self,section,orientation,role)
        
    

class setup(QtWidgets.QMainWindow):
    DOWN    = 1
    UP      = -1
    
    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.selectedCard = None
        self.selectedProfile = 0

    
    def mouseMoveEvent (self, eventQMouseEvent):
        if (eventQMouseEvent.x()>225 and eventQMouseEvent.x()<475) and (eventQMouseEvent.y()>145 and eventQMouseEvent.y()<395):
            self.setBalanceFader(eventQMouseEvent.x(), eventQMouseEvent.y())
   
    def setBalanceFader(self, x=0, y=0):
        if x==0:
            x=self.balanceHandle.x()+25
        if y==0:
            y=self.balanceHandle.y()+25
        self.balanceHandle.setGeometry(QtCore.QRect(x-25, y-25, 50, 50))
        balance=0
        fader=0
        if x<350:
            balance-=int((100/150)*(350-x)) #350-x
        elif x>350:
            balance+=int((100/150)*(x-350)) #x-350
            
        if y<270:
            fader-=int((100/150)*(270-y)) #231-y
        elif y>270:
            fader+=int((100/150)*(y-270)) #y-269
        self.parent.pa.setBalance(balance)
        self.parent.pa.setFader(fader)

    def loaded(self):
        self.equalizer=getattr(mod, "QPaeq")(self.parent)
        self.eq.setLayout(self.equalizer.layout())
        self.btnResetEQ.clicked.connect(lambda: self.equalizer.reset())

        self.btnSound.clicked.connect(lambda: self.parent.setPage(self.stack, 1))
        self.btnBalance.clicked.connect(lambda: self.parent.setPage(self.stack, 2))
        self.btnEqualizer.clicked.connect(lambda: self.parent.setPage(self.stack, 3))
        self.btnModule.clicked.connect(lambda: self.parent.setPage(self.stack, 5))
        
        self.balanceTouch.setAttribute(Qt.WA_AcceptTouchEvents)
        self.balanceTouch.setStyleSheet("background-color: #eee ;border-radius: 10px; border: 2px solid #000;")
        self.balanceTouch.setMouseTracking(True)
        self.balanceReset.clicked.connect(lambda: self.setBalanceFader(x=350))
        self.faderReset.clicked.connect(lambda: self.setBalanceFader(y=270))
        # Todo: settings setzen
        # self.balanceSlider.setValue(self.settings["balance"])
        
        self.btnBluetooth.clicked.connect(lambda: self.parent.setPage(self.stack, 4))
        
        self.btnReboot.clicked.connect(lambda: self.reboot())
        self.btnShutdown.clicked.connect(lambda: self.shutdown())
        self.btnQuit.clicked.connect(lambda: self.quit())
        self.btnFindBT.clicked.connect(lambda: self.getBTDevices())
        self.btnConnectBT.clicked.connect(lambda: self.connectDevice())
        self.btnUntrustBT.clicked.connect(lambda: self.untrustDevice())
        self.btnPhoneBook.clicked.connect(lambda: self.parent.mobile.loadPhonebook())
        self.btnBTAuto.clicked.connect(lambda: self.setAuto())
        self.btnBTAuto.setEnabled(False)
        self.tblBTDevices.itemClicked.connect(self.btDeviceChanged)
        self.btnEject.clicked.connect(self.eject)

        self.cardList.itemClicked.connect(self.setCard)
        self.profileList.itemSelectionChanged.connect(self.getPorts)
        self.portList.itemClicked.connect(lambda: self.setPort("sink"))
        self.sourceList.itemClicked.connect(lambda: self.setPort("source"))

        if self.settings["bt_auto"]:
            self.btnBTAuto.setStyleSheet("background-image: url(./images/bt_always_on.png);background-repeat: none; border: 0px;")
            #self.parent.schedule.every(2).seconds.do(self.connectMobile).tag('connectMobile')
            
        for path in glob("/media/pi/*/"):
            self.mountList.addItem(path)
        
        
        self.btDevices={}
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.cpu())
        self.timer.start(2000)
        
        self.btnUp.clicked.connect(lambda: self.moveCurrentRow(self.UP))
        self.btnDown.clicked.connect(lambda: self.moveCurrentRow(self.DOWN))
        self.btnSave.clicked.connect(lambda: self.saveConfig())
        
        self.setup = self.parent.setup
        self.showModules()
        
        
    def showModules(self):
        modules = self.parent.sortModules(self.setup.getElementsByTagName('module'))
        self.tableModel = tableModel(self)
        self.tableModel.itemChanged.connect(self.itemChanged)
        self.tableModel.header = ['Module', 'Label', 'Description']
        
        self.tableModel.modules = modules
        for module in modules:
            item = QtGui.QStandardItem(module.attributes["name"].value)
            item.setCheckable(True)
            if module.attributes["enabled"].value == "1":
                item.setCheckState(2)
            label = QtGui.QStandardItem(module.attributes["label"].value)
            description = QtGui.QStandardItem(module.attributes["description"].value)
            self.tableModel.appendRow([item, label, description])
        self.modules.setModel(self.tableModel)
        header = self.modules.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        
    def moveCurrentRow(self, direction=DOWN):
        if direction not in (self.DOWN, self.UP):
            return

        model = self.tableModel
        selModel = self.modules.selectionModel()
        selected = selModel.selectedRows()
        if not selected:
            return

        items = []
        indexes = sorted(selected, key=lambda x: x.row(), reverse=(direction==self.DOWN))

        for idx in indexes:
            items.append(model.itemFromIndex(idx))
            rowNum = idx.row()
            newRow = rowNum+direction
            if not (0 <= newRow < model.rowCount()):
                continue

            rowItems = model.takeRow(rowNum)
            model.insertRow(newRow, rowItems)

        selModel.clear()
        for item in items:
            selModel.select(item.index(), selModel.Select|selModel.Rows)
        
        modules = self.setup.getElementsByTagName('module')
        for row in range(self.tableModel.rowCount()):
            index = self.tableModel.index( row, 0 );
            for module in modules:
                if module.attributes["name"].value == index.data():
                    module.attributes["order"].value = str(row)
        
    def itemChanged(self, item):
        modules = self.setup.getElementsByTagName('module')
        for module in modules:
            if module.attributes["name"].value == item.text():
                module.attributes["enabled"].value = str(int(bool(item.checkState())))

        print("Item {!r} checkState: {}".format(item.text(), item.checkState()))
        
    def saveConfig(self):   
        self.parent.setup = self.setup
        self.parent.saveConfig()
        self.parent.stopPlayer()
        self.parent.readConfig()
        self.parent.switchModule(0)

        
        
    def connectMobile(self):
        if self.parent.mobile.getConnectedDevice() == False and self.settings["bt_device"] != "":
            self.parent.mobile.connect(self.settings["bt_device"])
        
    def focus(self):
        try:
            self.lblLan.setText(ni.ifaddresses('eth0')[2][0]['addr'])
        except:
            self.lblLan.setText("Nicht verbunden")
        try:
            self.lblWifi.setText(ni.ifaddresses('wlan0')[2][0]['addr'])
        except:
            self.lblWifi.setText("Nicht verbunden")
            
        if os.path.exists("/media/pi/pyCar/update.tar.gz"):
            self.btnUpdate.setEnabled(True)
            
        self.lblBTAddresse.setText(self.parent.mobile.getLocalAddress())
        
        mem = psutil.virtual_memory()
        ges = str(int(mem.total/1024/1024))
        use = str(int(mem.used/1024/1024))
        self.lblMemory.setText(use + " MB von " + ges + " MB genutzt")
        
        disk = psutil.disk_usage('/')
        ges = str(int(disk.total/1024/1024))
        use = str(int(disk.used/1024/1024))
        self.lblDisk1.setText(str(int(disk.percent)) + "% ("+use+" MB) von "+ges+" MB genutzt")
        
        disk = psutil.disk_usage('/media/pi/pyCar')
        ges = str(int(disk.total/1024/1024))
        use = str(int(disk.used/1024/1024))
        self.lblDisk2.setText(str(int(disk.percent)) + "% ("+use+" MB) von "+ges+" MB genutzt")
        self.readMounts()
        
        
    def eject(self):
        if self.settings["usb"] != "":
            call("sudo umount "+self.settings["usb"], shell=True)
            self.readMounts()
    
    def readMounts(self):
        self.mountList.clear()
        for index, path in enumerate(glob("/media/pi/*/")):
            self.mountList.addItem(path)
            if path == self.settings["usb"]:
                self.mountList.setCurrentIndex(index)
        
    def soundSettings(self):
        self.getSoundcards()
        self.getProfiles()
        
    def setCard(self):
        self.parent.pa.settings["profile"] = ""
        self.parent.pa.settings["port"]["sink"] = ""
        self.parent.pa.settings["port"]["source"] = ""
        self.getProfiles()       

    def getSoundcards(self):
        self.cardList.clear()
        cards=self.parent.pa.getCards()
        for index, card in enumerate(cards):
            if card["props"].get("alsa.card_name"):
                itm = QtWidgets.QListWidgetItem(card["props"]["alsa.card_name"])
                self.cardList.addItem(itm)
                if card["props"]["alsa.card_name"] == self.parent.pa.settings["card"]:
                    self.cardList.setCurrentRow(index)
        
    def getProfiles(self):
        self.profileList.clear()
        try:
            profiles = self.parent.pa.getProfiles(self.cardList.currentItem().text())
            for index, profile in enumerate(profiles):
                itm = QtWidgets.QListWidgetItem(profile.description)
                self.profileList.addItem(itm)
                if profile.description == self.parent.pa.settings["profile"]:
                    self.profileList.setCurrentRow(index)
            self.getPorts()
        except:
            pass
        
    def getPorts(self):
        ### SINKS ###
        self.portList.clear()
        self.parent.pa.setProfile(self.cardList.currentItem().text(), self.profileList.currentItem().text())
        ports = self.parent.pa.getPorts(self.cardList.currentItem().text())
        if ports != None:    
            for index, port in enumerate(ports):
                itm = QtWidgets.QListWidgetItem(port.description)
                self.portList.addItem(itm)
                if port.description == self.parent.pa.settings["port"]:
                    self.portList.setCurrentRow(index)

        ### SOURCES ###
        self.sourceList.clear()
        sources = self.parent.pa.getSource(self.cardList.currentItem().text())
        if sources != None:
            for source in sources:
                itm = QtWidgets.QListWidgetItem(source.description)
                self.sourceList.addItem(itm)
    
    def setPort(self, pType):
        if pType == "sink":
            port = self.portList.currentItem().text()
        else:
            port = self.sourceList.currentItem().text()
        self.parent.pa.setPort(pType, self.cardList.currentItem().text(), port)
        
    
    def setAuto(self):
        if self.settings["bt_auto"]:
            self.settings["bt_auto"] = 0
            self.settings["bt_device"] = ""
            self.settings["bt_name"] = ""
            self.btnBTAuto.setStyleSheet("background-image: url(./images/bt_always_off.png);background-repeat: none; border: 0px;")
            self.parent.schedule.clear('connectMobile')
        else:
            try:
                self.settings["bt_auto"] = 1
                self.settings["bt_device"] = self.tblBTDevices.item(self.tblBTDevices.currentRow(), 0).text()
                self.settings["bt_name"] = self.tblBTDevices.item(self.tblBTDevices.currentRow(), 1).text()
                self.btnBTAuto.setStyleSheet("background-image: url(./images/bt_always_on.png);background-repeat: none; border: 0px;")
                self.parent.schedule.every(2).seconds.do(self.connectMobile).tag('connectMobile')
            except:
                pass
    
    def getBTDevices(self):
        self.tblBTDevices.clear()
        self.tblBTDevices.setStyleSheet("QScrollBar {height:0px;}")
        self.btnFindBT.setText("Geräte suchen...")
        self.tblBTDevices.setRowCount(0)
        self.tblBTDevices.setColumnCount(3)
        self.tblBTDevices.setColumnWidth(0,230)
        self.tblBTDevices.setColumnWidth(1,265)
        self.tblBTDevices.setColumnWidth(2,150)
        self.tblBTDevices.setHorizontalHeaderLabels(['MAC-Adresse', 'Name', 'Status'])
        self.btnPhoneBook.setEnabled(False)
        self.btnConnectBT.setText("Gerät verbinden")
        self.btnConnectBT.setEnabled(False)
        self.btnUntrustBT.setEnabled(False)
        self.bttimer = QtCore.QTimer()
        self.bttimer.timeout.connect(self.findBTDevices)
        self.bttimer.start(1000)

    def findBTDevices(self):
        self.bttimer.stop()
        devices=self.parent.mobile.findNearBy()
        self.btnFindBT.setText("Geräte suchen")
        if devices != False:
            self.tblBTDevices.setRowCount(len(devices))
            c=0
            for device in devices:
                #print (str(c)+ " : " + device[0] + " = " + device[1])
                newitem = QtGui.QTableWidgetItem(device[0])
                self.tblBTDevices.setItem(c,0,newitem)
                newitem = QtGui.QTableWidgetItem(device[1])
                self.tblBTDevices.setItem(c,1,newitem)
                con=""
                if self.parent.mobile.getConnectedDevice()==device[0]:
                    con="Verbunden"
                newitem = QtGui.QTableWidgetItem(con)
                self.tblBTDevices.setItem(c,2,newitem)
                self.btDevices[c]=device[0]
                c+=1
            
    def btDeviceChanged(self):
        selected = self.btDevices[self.tblBTDevices.currentRow()]
        if self.parent.mobile.getConnectedDevice()==selected:
            self.btnConnectBT.setText("Gerät trennen")
            self.btnBTAuto.setEnabled(True)
            self.btnConnectBT.setEnabled(True)
            self.btnPhoneBook.setEnabled(True)
        else:
            if self.parent.mobile.isTrusted(selected) == False: # not trusted/paired
                self.btnConnectBT.setText("Gerät koppeln")
                self.btnConnectBT.setEnabled(True)
                self.btnBTAuto.setEnabled(False)
            else:
                self.btnPhoneBook.setEnabled(False)
                self.btnConnectBT.setText("Gerät verbinden")
                self.btnConnectBT.setEnabled(True)
                self.btnBTAuto.setEnabled(False)
        if self.parent.mobile.isTrusted(selected):
            self.btnUntrustBT.setEnabled(True)
        else:
            self.btnUntrustBT.setEnabled(False)
            
    def connectDevice(self):
        selectedDevice = self.btDevices[self.tblBTDevices.currentRow()]
        connectedDevice = self.parent.mobile.getConnectedDevice()
        if connectedDevice == False: # no device connected
            if self.parent.mobile.isTrusted(selectedDevice) == False: # not trusted/paired
                self.parent.mobile.pair(selectedDevice)
            else:
                self.parent.mobile.connect(selectedDevice)
                timeout = 0
                while connectedDevice == False or timeout<5:
                    connectedDevice = self.parent.mobile.getConnectedDevice()
                    time.sleep(1)
                    timeout+=1
                if connectedDevice == False:
                    self.tblBTDevices.item(self.tblBTDevices.currentRow(), 2).setText("Fehler")
                else:
                    self.tblBTDevices.item(self.tblBTDevices.currentRow(), 2).setText("Verbunden")
                    self.btnConnectBT.setText("Gerät trennen")
                    self.btnBTAuto.setEnabled(True)
        elif connectedDevice != selectedDevice:
            for row in range(0, self.tblBTDevices.rowCount()):
                if self.tblBTDevices.item(row, 0).text() == connectedDevice:
                    cr = row
            timeout = 0
            self.parent.mobile.disconnect(connectedDevice)
            while connectedDevice == self.parent.mobile.getConnectedDevice() or timeout<5:
                time.sleep(1)
                timeout+=1
            if self.parent.mobile.getConnectedDevice() == False:
                self.tblBTDevices.item(cr, 2).setText("")
                self.connectDevice()
            else:
                self.tblBTDevices.item(cr, 2).setText("Fehler")
                self.btnBTAuto.setEnabled(False)
        else:
            timeout = 0
            self.parent.mobile.disconnect(connectedDevice)
            self.btnBTAuto.setEnabled(False)
            while connectedDevice == self.parent.mobile.getConnectedDevice() or timeout<5:
                time.sleep(1)
                timeout+=1
            if self.parent.mobile.getConnectedDevice() == False:
                self.tblBTDevices.item(self.tblBTDevices.currentRow(), 2).setText("")
                self.btnConnectBT.setText("Gerät verbinden")
            else:
                self.tblBTDevices.item(self.tblBTDevices.currentRow(), 2).setText("Fehler")
                
                

        """
        if self.parent.phone.getConnectedDevice()==selected:
            self.parent.phone.disconnect(selected)
            time.sleep(3)
            if self.parent.phone.getConnectedDevice()==False:
                #settings["bluetooth"]["btdevice"]=""
                newitem = QtGui.QTableWidgetItem("")
                self.tblBTDevices.setItem(self.tblBTDevices.currentRow(),2,newitem)
                self.btnConnectBT.setText("Gerät verbinden")
                self.btnPhoneBook.setEnabled(False)
        else:
            if self.parent.phone.getConnectedDevice():
                self.parent.phone.disconnect(phone.getConnectedDevice())
                for i in range(0, len(self.btDevices)):
                    newitem = QtGui.QTableWidgetItem("")
                    self.tblBTDevices.setItem(i,2,newitem)
            self.parent.phone.connect(selected)
            #settings["bluetooth"]["btdevice"]=selected
            time.sleep(3)
            if self.parent.phone.getConnectedDevice():
                newitem = QtGui.QTableWidgetItem("Verbunden")
                self.tblBTDevices.setItem(self.tblBTDevices.currentRow(),2,newitem)
                self.btnConnectBT.setText("Gerät trennen")
                self.btnPhoneBook.setEnabled(True)
        #self.saveSettings("bluetooth", "btdevice", phone.getConnectedDevice())
        """
    def untrustDevice(self):
        selected = self.btDevices[self.tblBTDevices.currentRow()]
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Möchtest Du das Bluetoothdevice wirklich entfernen? Das Telefonbuch wird ebenfalls entfernt!")
        msg.setWindowTitle("Bluetoothgerät entfernen")
        msg.addButton(QtGui.QPushButton('Entfernen'), QtGui.QMessageBox.YesRole)
        msg.addButton(QtGui.QPushButton('Abbrechen'), QtGui.QMessageBox.NoRole)
        retval = msg.exec_()
        print ("value of pressed message box button:", retval)
        if retval==0:
            self.parent.mobile.untrust(selected)
            self.getBTDevices()

    def cpu(self):
        cpu = psutil.cpu_percent()
        self.lblCPU.setText(str(cpu) + "%")
        if self.settings["bt_auto"]:
            self.connectMobile()
            
    def reboot(self):
        self.parent.saveConfig()
        call("sudo reboot", shell=True)          
            
    def shutdown(self):
        self.parent.saveConfig()
        call("sudo shutdown -h now", shell=True)
        
    def quit(self):
        self.parent.saveConfig()
        exit()
        
        
        
        
        
        
        
        
        