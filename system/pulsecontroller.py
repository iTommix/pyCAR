import smbus, dbus, dbus.mainloop.glib
from pulsectl import *
from PyQt5 import QtCore, QtWidgets
from subprocess import call
from gi.repository import GLib


call(["pulseaudio -D"], shell=True)
pulse = Pulse('pyCAR')
pulse.module_load("module-equalizer-sink")
pulse.module_load("module-dbus-protocol")
mute = ["on", "off"]
maxVol=45


class EventThread(QtCore.QThread):
    def __init__(self, parent, eq, echo):
        super(EventThread, self).__init__(parent)
        self.eq = eq
        self.echo = echo
        bus = dbus.SessionBus()
        server_lookup = bus.get_object("org.PulseAudio1", "/org/pulseaudio/server_lookup1")
        address = server_lookup.Get("org.PulseAudio.ServerLookup1", "Address", dbus_interface="org.freedesktop.DBus.Properties")
        self.pulse_bus = dbus.connection.Connection(address)
        
    def run(self):
        pulse_core = self.pulse_bus.get_object(object_path='/org/pulseaudio/core1')
        pulse_core.ListenForSignal('org.PulseAudio.Core1.NewPlaybackStream', dbus.Array(signature='o'), dbus_interface='org.PulseAudio.Core1')
        self.pulse_bus.add_signal_receiver(self.callback, 'NewPlaybackStream')
        loop = GLib.MainLoop()
        loop.run()
        
    def callback(self, path):
        props = dbus.Interface(self.pulse_bus.get_object(object_path=path), dbus_interface='org.freedesktop.DBus.Properties')
        index = dbus.Int32(props.Get('org.PulseAudio.Core1.Stream', "Index"))
        self.setSink(index)
        
    def setSink(self, index):
        for sink in pulse.sink_input_list():
            if sink.index == index:
                if sink.proplist.get("media.role") and sink.proplist["media.role"] == "phone":
                    pulse.sink_input_move(index, self.echo)
                elif sink.proplist.get("media.role") and sink.proplist["media.role"] == "abstract":
                    for source_output in pulse.source_output_list():
                        if source_output.proplist.get("media.role") and source_output.proplist["media.role"] == "phone":
                            source_output_id = source_output.index
                    for source in pulse.source_list():
                        if (source.proplist.get("device.class") and source.proplist["device.class"] == "filter") and (source.proplist.get("device.intended_roles") and source.proplist["device.intended_roles"] == "phone"):
                            source_id = source.index
                    pulse.source_output_move(source_output_id, source_id) 
                    
                else:
                    pulse.sink_input_move(index, self.eq)
        
    
class Pulsecontroller():
    
    def __init__(self, parent):
        self.loweredModule = None
        self.parent = parent
        self.cardID = None
        self.equalizerID = None
        self.echoID = None
        self.microphoneID = None
        
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
        self.setMicVolume(self.settings["microphone"])
        self.setMicActive(False)
        
        if self.microphoneID != None:
            pulse.module_load("module-echo-cancel", "aec_method=webrtc")
        
        event = EventThread(self.parent, self.equalizerID, self.echoID)
        event.start()
        
        
        
        

        # Setup Volume for all streams and move to equalizer
        for module in self.parent.modules:
            if module != "pyCAR" and self.parent.modules[module]["instance"].settings.get("volume"):
                volume = self.parent.modules[module]["instance"].settings["volume"]
                for sink in pulse.sink_input_list():
                    try:
                        if sink.proplist[volume["property"]] == volume["identyfier"]:
                            pulse.sink_input_move(sink.index, self.equalizerID)
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
            
    
    def setMicVolume(self, volume):
        self.settings["microphone"]=volume
        for source in pulse.source_list():
            if source.proplist.get("alsa.card_name") and source.proplist["alsa.card_name"] == self.settings["card"] and source.proplist["device.class"] == "sound":
                pulse.volume_set_all_chans(source, volume/100)
                self.microphoneID = source.index
    
    def setMicActive(self, status):
        if self.microphoneID != None:
            pulse.mute(pulse.source_list()[self.microphoneID], not status)
            
            
    def mute(self):
        pulse.mute(pulse.sink_list()[self.cardID], not pulse.sink_list()[self.cardID].mute)
        button=self.parent.findChild(QtWidgets.QToolButton, "btnMute")
        button.setStyleSheet("background-image: url(./images/mute_"+str(mute[pulse.sink_list()[self.cardID].mute])+".png);background-repeat: none; border: 0px;")
            
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
            if "FFT based equalizer" in sink.description:
                self.equalizerID = sink.index            
            if sink.proplist.get("alsa.card_name") and sink.proplist["alsa.card_name"] == self.settings["card"]:
                self.cardID = sink.index
            if "echo cancelled" in sink.description:
                self.echoID = sink.index
        for sink in pulse.sink_input_list():
            if sink.name == "Equalized Stream":
                #pulse.sink_input_move(sink.index, self.cardID)
                eqStream = sink.index
            if sink.name == "Echo-Cancel Sink Stream":
                #pulse.sink_input_move(eqStream, self.echoID)
                pass
            if not sink.proplist.get("media.role") or (sink.proplist.get("media.role") and sink.proplist["media.role"] != "filter"):
                pulse.sink_input_move(sink.index, self.equalizerID)

            
        