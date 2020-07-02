import smbus, alsaaudio
from PyQt4 import QtCore, QtGui
i2c = smbus.SMBus(1)
max9744 = False
volume = 30
balance = 0
ismute = 0
mixer = None
parent = None
try:
    i2c.read_byte(0x4A)
    print("max9744 present")
    max9744=True
    from Adafruit_MAX9744 import MAX9744
    amp_f = MAX9744(0x4A)
    amp_r = MAX9744(0x4b)
except:
    print("max9744 NOT present")
    

def init(settings, mix):
    global volume, balance, mute, mixer
    volume = settings["volume"]
    balance = settings["balance"]
    ismute = settings["mute"]
    mixer = alsaaudio.Mixer(mix) 
    if max9744:
        #setVolume(volume)
        mixer.setvolume(100)
    else:
        mixer.setvolume(volume)

def setMixer(self, mix):
    mixer = alsaaudio.Mixer(mix)

       
def mute():
    global ismute
    button=parent.findChild(QtGui.QToolButton, "btnMute")
    if ismute==0:
        amp_f.set_volume(0)
        amp_r.set_volume(0)
        ismute = 1
        button.setStyleSheet("background-image: url(./images/mute_off.png);background-repeat: none; border: 0px;")
    else:
        ismute = 0
        setVolume(volume)
        button.setStyleSheet("background-image: url(./images/mute_on.png);background-repeat: none; border: 0px;")
    
def setVolume(value, showView=True):
    global volume
    print("Set Volume to", value)
    volume = value
    v=(63/100)*volume
    amp_f.set_volume(int(round(v)))
    amp_r.set_volume(int(round(v)))
    
def getVolume():
    global volume
    return volume
    