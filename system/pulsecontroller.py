import smbus
from pulsectl import *
from PyQt4 import QtCore, QtGui
from subprocess import call
from gi.repository import GLib

pulse = Pulse('pyCAR')
mute = ["on", "off"]
maxVol=45
cardID = None
equalizerID = None

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
        cmd = "/usr/bin/amixer -M set "+self.settings["alsaout"]+" 100%"
        call(cmd, shell=True)
        self.setFader(self.settings["fader"])
        self.setBalance(self.settings["balance"])
        # Setup Soundcard
        
        self.setProfile(self.settings["card"], self.settings["profile"])
        self.setPort("sink", self.settings["card"], self.settings["port"]["sink"])
        self.setPort("source", self.settings["card"], self.settings["port"]["source"])
        #self.setEqualizer()
        
        

        # Setup Volume for all streams and move to equalizer
        for module in self.parent.modules:
            if module != "pyCAR" and self.parent.modules[module]["instance"].settings.get("volume"):
                volume = self.parent.modules[module]["instance"].settings["volume"]
                for sink in pulse.sink_input_list():
                    try:
                        if sink.proplist[volume["property"]] == volume["identyfier"]:
                            pulse.sink_input_move(sink.index, equalizerID)
                    except:
                        pass
                self.setVolume(module)
                        
    def setVolume(self, module):
        volume = self.parent.modules[module]["instance"].settings["volume"]
        for sink in pulse.sink_input_list():
            try:
                if sink.proplist[volume["property"]] == volume["identyfier"]:
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
        for sink in pulse.sink_list():
            if sink.proplist.get("alsa.card_name") and sink.proplist["alsa.card_name"] == self.settings["card"]:
                pulse.volume_set(sink, volume)
        
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
        
        
    def getCards(self):
        cards=[]
        for card in pulse.card_list():
            c={"card": card, "props": card.proplist}
            cards.append(c)
        return cards
    
    def getProfiles(self, alsaName):
        for card in pulse.card_list():
            if card.proplist.get("alsa.card_name") and card.proplist["alsa.card_name"] == alsaName:
                return card.profile_list
                
    def getPorts(self, alsaName):
        for sink in pulse.sink_list():
            if sink.proplist.get("alsa.card_name") and sink.proplist["alsa.card_name"] == alsaName:
                return sink.port_list
            
    def getSource(self, alsaName):
        for source in pulse.source_list():
            if source.proplist.get("alsa.card_name") and source.proplist["alsa.card_name"] == alsaName and source.proplist["device.class"] == "sound":
                return source.port_list
            
    def setProfile(self, alsaName, profileName):
        self.settings["card"] = alsaName
        self.settings["profile"] = profileName
        for card in pulse.card_list():
            if card.proplist.get("alsa.card_name") and card.proplist["alsa.card_name"] == alsaName:
                for profile in card.profile_list:
                    if profile.description == profileName:
                        pulse.card_profile_set(card, profile)
                        
    def setPort(self, plist, alsaName, portName):
        print(plist)
        self.settings["port"][plist] = portName
        if plist == "sink":
            pulseList = pulse.sink_list()
        else:
            pulseList = pulse.source_list()
        
        for item in pulseList:
            if item.proplist.get("alsa.card_name") and item.proplist["alsa.card_name"] == alsaName:
                for port in item.port_list:
                    if port.description == portName:
                        pulse.port_set(item, port)
        self.setEqualizer()
    
    def setEqualizer(self):
        for sink in pulse.sink_list():
            if sink.proplist["device.class"] == "filter":
                equalizerID = sink.index
            if sink.proplist.get("alsa.card_name") and sink.proplist["alsa.card_name"] == self.settings["card"]:
                cardID = sink.index
        for sink in pulse.sink_input_list():
            if sink.proplist.get("media.role") and sink.proplist["media.role"]=="filter" and cardID != None:
                pulse.sink_input_move(sink.index, cardID)
        