from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
import sys, os, json, time, dbus, sqlite3



path=os.path.dirname(os.path.abspath( __file__ )).rsplit('/', 1)

class phone(QtWidgets.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)
       
        self.call=0
        self.callPath=None
        self.path=None
        self.phoneBookLoaded=False
        self.micActive = False
        
    def loaded(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.detectIncomingCall())
        self.timer.start(500)
        
        self.phonebookList.verticalScrollBar().setStyleSheet("QScrollBar:vertical {width:50px}");
        self.tblPhoneNumbers.verticalScrollBar().setStyleSheet("QScrollBar:vertical {width:50px}");
        
        self.phonebookList.setVerticalScrollMode(self.phonebookList.ScrollPerPixel)
        QtWidgets.QScroller.grabGesture(self.phonebookList.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)
        
        for number in range(0,10):
            button = getattr(self, "btnPhone"+str(number))
            button.clicked.connect(lambda: self.phoneButton())
            
        self.btnPhone10.clicked.connect(lambda: self.phoneButton('*'))
        self.btnPhone11.clicked.connect(lambda: self.phoneButton('#'))
        self.btnDelete.clicked.connect(lambda: self.phoneDelete())
        self.btnCallNumber.clicked.connect(lambda: self.makePhoneCall())
        self.btnCallNumber.setIcon(QIcon("./images/call.png"));
        self.btnCallNumber.setIconSize(QtCore.QSize(100,100))
        
        self.btnPhonebook.setIcon(QIcon("./images/phonebook.png"));
        self.btnPhonebook.setIconSize(QtCore.QSize(100,100))
        self.btnLoadPhonebook.clicked.connect(lambda: self.loadPhonebook())
        
        self.phonebookList.itemClicked.connect(self.PhoneNumbers)
        self.tblPhoneNumbers.itemClicked.connect(self.phoneNumberSelected)
        self.btnPhonebook.clicked.connect(lambda: self.parent.setPage(self.stack, 1))

        
        self.btnCallAnswer.clicked.connect(lambda: self.answerRejectCall('answer'))
        self.btnCallReject.clicked.connect(lambda: self.answerRejectCall('reject'))
    
    def focus(self):
        self.Phonebook()
    
    def loadPhonebook(self):
        self.parent.mobile.loadPhonebook()
        self.Phonebook()
    
    def phoneButton(self):
        button=self.sender()
        value=button.objectName().replace("btnPhone","")
        self.lblPhoneNumber.setText(self.lblPhoneNumber.text() + value)
        
    def phoneDelete(self):
        number=self.lblPhoneNumber.text()
        self.lblPhoneNumber.setText(number[:-1])
        
    def hideButtonsOnCall(self, hide):
        if hide == True:
            for number in range(0,10):
                button = getattr(self, "btnPhone"+str(number))
                button.setVisible(False)
            self.btnPhone10.setVisible(False)
            self.btnPhone11.setVisible(False)
            self.btnPhonebook.setVisible(False)
            self.btnDelete.setVisible(False)
            self.btnCallNumber.setIcon(QIcon("./images/callend.png"));
            self.btnCallNumber.setGeometry(QtCore.QRect(300, 210, 100, 100))           
        else:
            self.btnCallNumber.setGeometry(QtCore.QRect(40, 210, 100, 100))
            for number in range(0,10):
                button = getattr(self, "btnPhone"+str(number))
                button.setVisible(True)
            self.btnPhone10.setVisible(True)
            self.btnPhone11.setVisible(True)
            self.btnPhonebook.setVisible(True)
            self.btnDelete.setVisible(True)
            
            self.btnCallAnswer.setVisible(True)
            self.btnCallReject.setGeometry(QtCore.QRect(540, 210, 100, 100))
            
                
    def makePhoneCall(self):
        bus = dbus.SystemBus()
        if self.call==0:
            self.parent.stopPlayer()
            self.hideButtonsOnCall(True)
            self.parent.volume.setVolume(self.settings["volume"], False)

            print("Call to " + self.lblPhoneNumber.text())
            manager = dbus.Interface(bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
            modems = manager.GetModems()
            for path, properties in modems:
                mac = path.replace("/hfp/org/bluez/hci0/dev_","").replace("_", ":")
                if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                        continue
            #modem = modems[0][0]      
            hide_callerid = "default"
            number = self.lblPhoneNumber.text()
            vcm = dbus.Interface(bus.get_object('org.ofono', path), 'org.ofono.VoiceCallManager')
            self.callPath = vcm.Dial(number, hide_callerid)
            #self.btnCallNumber.setStyleSheet("background-image: url(./images/callend.png);background-repeat: none;border: 0px;")
            self.call=1
        else:
            caller = dbus.Interface(bus.get_object('org.ofono', self.callPath), 'org.ofono.VoiceCall')
            caller.Hangup()
            self.endCall()
            
    def endCall(self):
        self.call=0
        self.micActive = False
        self.parent.pa.setMicActive(False)
        self.btnCallNumber.setIcon(QIcon("./images/call.png"));
        self.hideButtonsOnCall(False)
        #self.btnCallNumber.setStyleSheet("background-image: url(./images/call.png);background-repeat: none;border: 0px;")
        self.lblPhoneNumber.setText("")
        self.parent.resume()
        
    def answerRejectCall(self, mode):
        #path = self.getPath()
        bus = dbus.SystemBus()
        call = dbus.Interface(bus.get_object('org.ofono', self.path),'org.ofono.VoiceCall')
        if mode=='answer':
            call.Answer()
            self.btnCallAnswer.setVisible(False)
            self.btnCallReject.setGeometry(QtCore.QRect(300, 210, 100, 100))
            self.btnCallAnswer
            self.call=1
        else:
            call.Hangup()
            
    
    def detectIncomingCall(self):
        if self.parent.mobile.getConnectedDevice()==False:
            return
        if self.phoneBookLoaded==False: self.Phonebook()
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.ofono', '/'),'org.ofono.Manager')
        modems = manager.GetModems()
        for path, properties in modems:
            #print("[ %s ]" % (path))
            mac = path.replace("/hfp/org/bluez/hci0/dev_","").replace("_", ":")
            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                    continue
            mgr = dbus.Interface(bus.get_object('org.ofono', path),'org.ofono.VoiceCallManager')
            calls = mgr.GetCalls()
            callState=""
            for path, properties in calls:
                self.path=path
                callState = properties["State"]
                #print("[ %s ] %s" % (path, callState))
                print(callState)
                if callState=='active':
                    self.call=1
                    if self.micActive == False:
                        self.micActive = True
                        self.parent.pa.setMicActive(True)
                if callState=='incoming':
                    if self.call==0: self.parent.stopPlayer()
                    self.call=1
                    if self.parent.mainFrame.currentIndex() != self.parent.modules["phone"]["deck"]:
                        if properties["LineIdentification"] != "":
                            number, ntype = self.getCaller(properties["LineIdentification"])
                        else:
                            number = "Anonym"
                            ntype=""
                        self.lblPhoneIncomingNumber.setText(number)
                        self.lblPhoneIncomingType.setText(ntype)
                        self.parent.setPage(self.stack, 3)
                        self.parent.mainFrame.setCurrentIndex(self.parent.modules["phone"]["deck"])
                        self.parent.active="phone"
                        self.parent.pa.setVolume("phone")
   
            if callState=="" and self.call==1:
                self.parent.setPage(self.stack, 0)
                self.endCall()

    def Phonebook(self):
        self.phonebookList.clear()
        if self.parent.mobile.getConnectedDevice():
            device=self.parent.mobile.getConnectedDevice()
            if(device):
                database="/media/pi/pyCar/Phone/Phonebooks/" + device.replace(":", "_") + ".db"
                if(os.path.isfile(database)):
                    conn = sqlite3.connect(database)
                    cursor = conn.cursor()
                    for row in cursor.execute("SELECT uid, surname, first_name  FROM names ORDER BY surname, first_name"):
                        if row[1]!="":
                            name=row[1]+", "+row[2]
                        else:
                            name=row[2]
                        itm = QtWidgets.QListWidgetItem(name);
                        itm.setWhatsThis(row[0])
                        self.phonebookList.addItem(itm)
                    self.phoneBookLoaded=True
                else:
                    self.phoneBookLoaded=False
                
    def getPhonebook():
        self.parent.mobile.getPhonebook()
        self.Phonebook()
    
    def PhoneNumbers(self):  
        self.tblPhoneNumbers.clear()
        self.tblPhoneNumbers.setColumnWidth(0,180)
        self.tblPhoneNumbers.setColumnWidth(1,400)
        uid=self.phonebookList.currentItem().whatsThis()
        print(uid)
        device=self.parent.mobile.getConnectedDevice()
        print(device)
        database="/media/pi/pyCar/Phone/Phonebooks/" + device.replace(":", "_") + ".db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        c=0
        cursor.execute("SELECT count(*) FROM numbers WHERE uid='"+uid+"' AND number LIKE '+%'")
        rows = cursor.fetchone()
        self.tblPhoneNumbers.setRowCount(rows[0])
        for row in cursor.execute("SELECT type, number FROM numbers WHERE uid='"+uid+"' AND number LIKE '+%' ORDER BY type"):
            newitem = QtWidgets.QTableWidgetItem(row[0])
            self.tblPhoneNumbers.setItem(c,0,newitem)
            newitem = QtWidgets.QTableWidgetItem(row[1])
            self.tblPhoneNumbers.setItem(c,1,newitem)
            c+=1
        #self.tblPhoneNumbers.resizeColumnsToContents()
        self.lblPhoneName.setText(self.phonebookList.currentItem().text())      
        self.parent.setPage(self.stack, 2)

        
        
    def getCaller(self, number):
        device=self.parent.mobile.getConnectedDevice()
        database="/media/pi/pyCar/Phone/Phonebooks/" + device.replace(":", "_") + ".db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT nu.uid, nu.type, na.first_name, na.surname FROM numbers nu LEFT JOIN names na ON na.uid=nu.uid WHERE nu.number='"+ number +"'")
        row=cursor.fetchone()
        try:
            return row[2]+" "+row[3], row[1]
        except:
            return number, ""
        
    def phoneNumberSelected(self):
        number = self.tblPhoneNumbers.item(self.tblPhoneNumbers.currentRow(),1).text()
        self.lblPhoneNumber.setText("+"+str(self.getNumber(number)))
        #self.frame.setGeometry(QtCore.QRect(0, 0, 2100, 480))
        self.parent.setPage(self.stack, 0)
        self.makePhoneCall()
        
    def getNumber(self, number):
        return int(''.join(ele for ele in number if ele.isdigit()))
    
    def getPath(self):
        device=self.parent.mobile.getConnectedDevice()
        return "/hfp/org/bluez/hci0/dev_"+device.replace(":","_")

        
        
        
        
def main():
    app = QtGui.QApplication(sys.argv)
    form = pyphone()
    form.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()