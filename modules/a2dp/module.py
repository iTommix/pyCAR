from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QIcon
import sys, os, json, time, dbus
from xml.dom import minidom

path=os.path.dirname(os.path.abspath( __file__ )).rsplit('/', 1)
#form_class = uic.loadUiType(path[0]+"/"+path[1]+"/gui.ui")[0]

class a2dp(QtGui.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        
        
        
    def loaded(self):
        self.path = self.settings["a2dpPath"]
        self.musicSlider.setEnabled(False)
        self.btn_Select.clicked.connect(lambda: self.showBrowser())
        self.musicList.itemClicked.connect(self.select)
        self.musicList.verticalScrollBar().setStyleSheet("QScrollBar:vertical {width:50px}")
        self.btn_Repeat.clicked.connect(lambda: self.setProperties("repeat"))
        self.btn_Shuffle.clicked.connect(lambda: self.setProperties("shuffle"))
        self.btn_Forward.clicked.connect(lambda: self.function('Next'))
        self.btn_Backward.clicked.connect(lambda: self.function('Previous'))
        self.btn_Seekforward.clicked.connect(lambda: self.function('FastForward'))
        self.btn_Seekbackward.clicked.connect(lambda: self.function('Rewind'))
        self.btn_Play.clicked.connect(lambda: self.togglePlay())

        self.statusTimer = QtCore.QTimer()
        self.statusTimer.timeout.connect(self.status)
        self.statusTimer.start(500)
        
        self.a2dpPlayer='player0'
        self.setPlayer()
        
    def focus(self):
        self.browser()
        
    def mute(self):
        pass
            
    def pause(self):
        device=self.parent.mobile.getConnectedDevice()
        if (device):
            self.function("Pause")
    
    def stop(self):
        self.pause()
            
    def play(self):
        device=self.parent.mobile.getConnectedDevice()
        if (device):
            self.function("Play")
            
    def togglePlay(self):
        device=self.parent.mobile.getConnectedDevice()
        if (device):
            bus = dbus.SystemBus()
            props = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0/dev_' + device.replace(":","_") + '/' + self.a2dpPlayer), 'org.freedesktop.DBus.Properties')
            status=dbus.String(props.Get('org.bluez.MediaPlayer1', "Status"))
            if status=="playing":
                self.function("Pause")
            else:
                self.function("Play")

    def showBrowser(self):
        self.browser()
        self.parent.setPage(self.stack, 1)
    
    def function(self, function):
        device=self.parent.mobile.getConnectedDevice()
        if(device):
            bus = dbus.SystemBus()
            player = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0/dev_' + device.replace(":","_") + '/' + self.a2dpPlayer), 'org.bluez.MediaPlayer1')
            if function=='Play':
                # Mute everything else:
                #self.stopMusic()
                player.Play()
            if function=="Pause":
                player.Pause()

            if function=='Next':
                player.Next()
            elif function=='Previous':
                player.Previous()
            elif function=='FastForward':
                player.FastForward()
                self.btn_Play.setStyleSheet("background-image: url(./images/play.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
            elif function=='Rewind':
                player.Rewind()
                self.btn_Play.setStyleSheet("background-image: url(./images/play.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
              
        
    def status(self):
        device=self.parent.mobile.getConnectedDevice()
        if device!=False:
            self.setPlayer()
            self.stack.setEnabled(1)
            self.lbl_Phone.setText(self.parent.mobile.getConnectedName(device))
            try:
                bus = dbus.SystemBus()
                props = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0/dev_' + device.replace(":","_") + '/' + self.a2dpPlayer), 'org.freedesktop.DBus.Properties')
                status=dbus.String(props.Get('org.bluez.MediaPlayer1', "Status"))
                if status=="playing":
                    self.btn_Play.setStyleSheet("background-image: url(./images/pause.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
                    playing = dbus.Dictionary(props.Get('org.bluez.MediaPlayer1', "Track"))
                    position=dbus.String(props.Get('org.bluez.MediaPlayer1', "Position"))
                    self.lbl_Time_left.setText(self.parent.getSongLength((playing["Duration"]-int(position))/1000))
                    self.lbl_Time_pos.setText(self.parent.getSongLength(int(position)/1000))
                    self.musicSlider.setMaximum(playing["Duration"]/1000)
                    self.musicSlider.setValue(int(position)/1000)
                    self.lbl_Artist.setText(playing["Artist"])
                    self.lbl_Title.setText(playing["Title"])
                    self.lbl_Album.setText(playing["Album"])
                    self.parent.setInfo(playing["Artist"], playing["Title"])
                elif status=="paused":
                    self.btn_Play.setStyleSheet("background-image: url(./images/play.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center") 
            except:
                pass
        else:
            self.lbl_Phone.setText("Nicht verbunden")
            self.stack.setEnabled(0)

    def setProperties(self, prop):
        device=self.parent.mobile.getConnectedDevice()
        bus = dbus.SystemBus()
        props = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0/dev_' + device.replace(":","_") + '/' + self.a2dpPlayer), 'org.freedesktop.DBus.Properties')
        if prop=="repeat":
            #off, singletrack, alltracks
            if self.settings["repeat"]==0:
                self.settings["repeat"]=1
                self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat1.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
                value="singletrack"
            elif self.settings["repeat"]==1:
                self.settings["repeat"]=2
                self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 2px solid #e42659;background-position: center")
                value="alltracks"
            else:
                self.settings["repeat"]=0
                self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
                value="off"
            props.Set('org.bluez.MediaPlayer1', "Repeat", value)
        if prop=="shuffle":
            #off, alltracks
            if self.settings["shuffle"]==0:
                self.settings["shuffle"]=1
                self.btn_Shuffle.setStyleSheet("background-image: url(./images/shuffle.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 2px solid #e42659;background-position: center")
                value="alltracks"
            else:
                self.settings["shuffle"]=0
                self.btn_Shuffle.setStyleSheet("background-image: url(./images/shuffle.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border:0px;background-position: center")
                value="off"
            props.Set('org.bluez.MediaPlayer1', "Shuffle", value)
        
        
    def browser(self):
        device=self.parent.mobile.getConnectedDevice()
        if device:
            try:
                bus = dbus.SystemBus()
                props = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0/dev_' + device.replace(":","_") + '/' + self.a2dpPlayer), 'org.bluez.MediaFolder1')
                path="/org/bluez/hci0/dev_" + device.replace(":","_") + "/" + self.a2dpPlayer + self.path
                props.ChangeFolder(path)
                items=json.loads(json.dumps(props.ListItems(''), indent=2))
                self.musicList.clear()
                self.musicList.clearSelection()
                if len(self.path.split("/"))>2:
                    itm = QtGui.QListWidgetItem("Zurück");
                    itm.setIcon(QIcon("./images/folder_up.png"));
                    itm.setWhatsThis("-")
                    self.musicList.addItem(itm);
                
                for key in items.keys():
                    parts=os.path.split(os.path.abspath(items[key]["Name"]))
                    itm = QtGui.QListWidgetItem(parts[1]);
                    im="./images/folder.png"
                    if items[key]["Playable"]==True: im="./images/song.png"
                    itm.setIcon(QIcon(im));
                    itm.setWhatsThis(key)
                    itm.setStatusTip(str(items[key]["Playable"]))
                    self.musicList.addItem(itm);
            except:
                #phone.disconnect(device)
                pass
            
    def select(self):
        device=self.parent.mobile.getConnectedDevice()
        playable=self.musicList.currentItem().statusTip()
        path=self.musicList.currentItem().whatsThis()
        print(playable, path)
        if path=="-":
            ca=self.lbl_currentAlbum.text().rsplit('/', 1)
            self.lbl_currentAlbum.setText(ca[0])
        else:
            if playable=="0":
                self.lbl_currentAlbum.setText(self.lbl_currentAlbum.text()+"/"+self.musicList.currentItem().text())
        bus = dbus.SystemBus()
        if playable=="1":
            player = dbus.Interface(bus.get_object('org.bluez', path), 'org.bluez.MediaItem1')
            player.Play()
            self.parent.setPage(self.stack, 0)
        else:
            if path=="-":
                path=self.path
                parts=path.rsplit('/', 1)
                newPath=parts[0]
            else:
                newPath=path.replace("/org/bluez/hci0/dev_" + device.replace(":","_") + "/" + self.a2dpPlayer, "")
            self.path=newPath
            self.browser()

    def setPlayer(self):
        device=self.parent.mobile.getConnectedDevice()
        if (device):
            bus = dbus.SystemBus()
            introspect = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0/dev_' + device.replace(":","_")), 'org.freedesktop.DBus.Introspectable')
            dom = minidom.parseString(introspect.Introspect())
            root = dom.documentElement
            for node in root.childNodes:
                if 'player' in node.attributes['name'].value:
                    self.a2dpPlayer=node.attributes['name'].value        
        
def main():
    app = QtGui.QApplication(sys.argv)
    form = pya2dp()
    form.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()