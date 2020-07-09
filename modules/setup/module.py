from PyQt4 import Qt, QtCore, QtGui, uic
import os, netifaces as ni, psutil, time, alsaaudio, pulsectl
from subprocess import call
from xml.dom import minidom

path=os.path.dirname(os.path.abspath( __file__ ))
form_class = uic.loadUiType(path+"/gui.ui")[0]
pulse = pulsectl.Pulse('pyCAR')

class tableModel(QtGui.QStandardItemModel):
    def __init__(self,datain,parent=None,*args):
        QtGui.QStandardItemModel.__init__(self,parent,*args)
        self.header = None
        self.modules = None
        
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
        
    def itemChanged(self, item):
        print(item)
        print("Item {!r} checkState: {}".format(item.text(), item.checkState())) 

class setup(QtGui.QMainWindow, form_class):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        self.selectedCard = None
        self.selectedProfile = 0
        
        
        
        
    def loaded(self):
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
        self.balanceReset.clicked.connect(lambda: self.balanceSlider.setValue(0))
        self.soundcards.activated.connect(self.getMixer)
        self.cardprofile.activated.connect(self.setProfile)
        self.cardmixer.activated.connect(self.setMixer)
        self.balanceSlider.valueChanged.connect(lambda: self.balance())
        if self.settings["bt_auto"]:
            self.btnBTAuto.setStyleSheet("background-image: url(./images/bt_always_on.png);background-repeat: none; border: 0px;")
            self.parent.schedule.every(2).seconds.do(self.connectMobile).tag('connectMobile')
            
        self.balanceSlider.setValue(self.settings["balance"])
        
        self.getSoundcards()
        self.btDevices={}
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.cpu())
        self.timer.start(1000)
        
        # Modules
        dom = minidom.parse('./system/config.xml')
        modules = self.parent.sortModules(dom.getElementsByTagName('module'))
        self.tableModel = tableModel(self)
        self.tableModel.header = ['Enabled', 'Name', 'Label']
        self.tableModel.modules = modules
        for module in modules:
            item = QtGui.QStandardItem()
            item.setCheckable(True)
            if module.attributes["enabled"].value == "1":
                item.setCheckState(2)
            name = QtGui.QStandardItem(module.attributes["name"].value)
            label = QtGui.QStandardItem(module.attributes["label"].value)
            self.tableModel.appendRow([item, name, label])
        self.modules.setModel(self.tableModel)
        
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
        
    def balance(self):
        self.settings["balance"] = self.balanceSlider.value()
        self.parent.volume.setBalance(self.balanceSlider.value())
        self.parent.volume.setVolume()

    def getSoundcards(self):
        current = 0
        i=0
        for z in reversed(alsaaudio.card_indexes()):
            (name, longname) = alsaaudio.card_name(i)
            #print("  %d: %s (%s)" % (i, name, longname))
            self.soundcards.addItem(name, z)
            if self.settings["card"] == name:
                current=i
            i=i+1
        self.soundcards.setCurrentIndex(current)
        self.getMixer()
            
    def getProfile(self):
        self.cardprofile.clear()
        i=0
        for z in reversed(alsaaudio.card_indexes()):
            card = pulse.card_list()[i]
            (name, longname) = alsaaudio.card_name(z)
            if name == self.soundcards.currentText():
                index = 0
                for profile in card.profile_list:
                    self.cardprofile.addItem(profile.description)
                    if profile.description == self.settings["profile"]:
                        pulse.card_profile_set(self.selectedCard, self.selectedCard.profile_list[index])
                        self.selectedProfile = index
                    index = index+1
            i=i+1
        self.cardprofile.setCurrentIndex(self.selectedProfile)
        
    def setProfile(self):
        #print(self.selectedCard)
        pulse.card_profile_set(self.selectedCard, self.selectedCard.profile_list[self.cardprofile.currentIndex()])
    
    def setMixer(self):
        self.parent.volume.setMixer(self.cardmixer.currentText())
    
    def getMixer(self):
        i=0
        selected=0
        for z in reversed(alsaaudio.card_indexes()):
            card = pulse.card_list()[i]
            (name, longname) = alsaaudio.card_name(z)
            if name == self.soundcards.currentText():
                #pulse.card_profile_set(card, card.profile_list[self.selectedProfile])
                self.selectedCard = card
                selected = z
            else:
                pulse.card_profile_set(card, 'off')
            i=i+1

        self.cardmixer.clear()
        current = 0
        i = 0
        for name in alsaaudio.mixers(selected):
            #print("  '%s'" % name)
            if self.settings["mixer"] == name:
                current=i
                self.parent.volume.setMixer(name)
            self.cardmixer.addItem(name)
            i=i+1
        self.cardmixer.setCurrentIndex(current)
        self.getProfile()
            
    
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
        
    def reboot(self):
        call("sudo reboot", shell=True)          
            
    def shutdown(self):
        call("sudo shutdown -h now", shell=True)
        
    def quit(self):
        call("sudo killall navit &", shell=True)
        exit()
        
        
        
        
        
        
        
        
        