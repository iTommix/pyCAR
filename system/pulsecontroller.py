import smbus
from pulsectl import *
from PyQt4 import QtCore, QtGui
from subprocess import call
from gi.repository import GLib

pulse = Pulse('pyCAR')
mute = ["on", "off"]
maxVol=45

class Pulsecontroller():
    
    def __init__(self, parent):
        self.loweredModule = None
        self.parent = parent
        i2c = smbus.SMBus(1)
        try:
            i2c.read_byte(0x4A)
            print("max9744 present")
            self.max9744 = True
            from Adafruit_MAX9744 import MAX9744
            self.amp_f = MAX9744(0x4A)
            self.amp_r = MAX9744(0x4b)
        except:
            self.max9744 = False
        
        
    def load(self, setup):
        self.settings = setup
        cmd = "/usr/bin/amixer -M set "+self.settings["alsa"]+" 100%"
        call(cmd, shell=True)
        self.setFader(self.settings["fader"])
        self.setBalance(self.settings["balance"])
        # Setup Soundcard
        for card in pulse.card_list():
            if card.index == self.settings["card"]:
                for profile in card.profile_list:
                    if profile.description == self.settings["profile"]:
                        pulse.card_profile_set(card, profile)
                for port in card.port_list:
                    if port.description == self.settings["port"]:
                        #pulse.port_set(card, port)
                        pass
        # Setup Volume for all streams 
        for module in self.parent.modules:
            try:
                if self.parent.modules[module]["instance"].settings["volume"]:
                    self.setVolume(module)
            except:
                pass
                        
    def setVolume(self, module):
        for sink in pulse.sink_list():
            if sink.proplist["device.class"] == "filter":
                equalizerID = sink.index
        
        volume = self.parent.modules[module]["instance"].settings["volume"]
        for sink in pulse.sink_input_list():
            try:
                if sink.proplist[volume["property"]] == volume["identyfier"]:
                    pulse.sink_input_move(sink.index, equalizerID)
                    pulse.volume_set_all_chans(sink, volume["value"]/100)
            except:
                pass
            
            
    def mute(self):
        pulse.mute(pulse.sink_list()[self.settings["card"]], not pulse.sink_list()[self.settings["card"]].mute)
        button=self.parent.findChild(QtGui.QToolButton, "btnMute")
        button.setStyleSheet("background-image: url(./images/mute_"+str(mute[pulse.sink_list()[self.settings["card"]].mute])+".png);background-repeat: none; border: 0px;")
            
    def setBalance(self, balance):
        self.settings["balance"]=balance
        if balance < 0:
            r=(100-abs(balance))/100
            l=1.0
        elif balance > 0:
            r=1.0
            l=(100-balance)/100
        else:
            r=1.0
            l=1.0
            
        print(r , l)
        volume = PulseVolumeInfo([l, r])
        pulse.volume_set(pulse.sink_list()[self.settings["card"]], volume)
        
    def setFader(self, fader):
        if self.max9744:
            self.settings["fader"]=fader
            if fader<0:
                front=maxVol
                rear=(maxVol/82)*(82-abs(fader))
            elif fader>0:
                front=(maxVol/82)*(82-fader)
                rear=maxVol
            else:
                front=maxVol
                rear=maxVol
            self.amp_f.set_volume(int(front))
            self.amp_r.set_volume(int(rear))
            
    def lowerVolume(self, sender):
        if self.parent.player != None and self.parent.player != sender:
            self.loweredModule = self.parent.player
            volume = self.parent.modules[self.parent.player]["instance"].settings["volume"]
            for sink in pulse.sink_input_list():
                try:
                    if sink.proplist[volume["property"]] == volume["identyfier"]:
                        nv = volume["value"]-(volume["value"]/100*40)
                        pulse.volume_set_all_chans(sink, nv/100)
                except:
                    pass
        
    def riseVolume(self):
        if self.loweredModule != None:
            self.setVolume(self.loweredModule)
        
            