import smbus, alsaaudio
from PyQt4 import QtCore, QtGui
from subprocess import call
i2c = smbus.SMBus(1)
max9744 = False
volume = 0
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
    amp_f.set_volume(45)
    amp_r.set_volume(45)
except:
    print("max9744 NOT present")
    

def init(settings, mix):
    global volume, balance, mute, mixer
    volume = settings["volume"]
    balance = settings["balance"]
    ismute = settings["mute"]
    mixer = alsaaudio.Mixer(mix)
    """
    if max9744:
        setVolume(volume)
        #mixer.setvolume(100)
    else:
        mixer.setvolume(volume)
    """

def setMixer(mix):
    global mixer
    mixer = alsaaudio.Mixer(mix)

def setBalance(value):
    global balance
    balance = value
       
def mute():
    global ismute
    button=parent.findChild(QtGui.QToolButton, "btnMute")
    if ismute==0:
        cmd = "/usr/bin/amixer -M set Headphone 0%,0%"
        call(cmd, shell=True)
        ismute = 1
        button.setStyleSheet("background-image: url(./images/mute_off.png);background-repeat: none; border: 0px;")
    else:
        ismute = 0
        setVolume(volume)
        button.setStyleSheet("background-image: url(./images/mute_on.png);background-repeat: none; border: 0px;")
    
def setVolume(value=None, showView=True):
    global volume
    if value == None:
        value = volume
    print("Set Volume to", value)
    volume = value
    # calculate the balance
    if balance < 0:
        r=(value/100)*(100-abs(balance))
        l=value
    elif balance > 0:
        r=value
        l=(value/100)*(100-balance)
    else:
        r=value
        l=value
        
    print(balance, int(l), int(r))
    cmd = "/usr/bin/amixer -M set Headphone "+str(int(l))+"%,"+str(int(r))+"%"
    call(cmd, shell=True)
    """
    v=(63/100)*volume
    amp_f.set_volume(int(round(v)))
    amp_r.set_volume(int(round(v)))
    """
    
def getVolume():
    global volume
    return volume
    