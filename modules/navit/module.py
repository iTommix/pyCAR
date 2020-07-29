import dbus
from dbus.mainloop.glib import DBusGMainLoop
import subprocess, time, os, sys
from PyQt4 import QtCore, QtGui, uic
from espeak import espeak

path=os.path.dirname(os.path.abspath( __file__ ))


class navit(QtGui.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        self.stack = None
        self.lastSpeech = None
        process = subprocess.Popen(['navit'],stdout=subprocess.PIPE, shell=True)
        pid = str(process.pid)
        cmd='xwininfo -name \'Navit\' | sed -e \'s/^ *//\' | grep -E "Window id" | awk \'{ print $4 }\''
        self.wid='';
        while self.wid=="" :
            proc = subprocess.check_output(cmd, shell=True)
            self.wid=proc.decode("utf-8").replace("\n","");
    
    def focus(self):
        if self.lastSpeech != None:
            self.speech(self.lastSpeech)
    

    def loaded(self):
        espeak.set_voice(self.settings["voice"])
        espeak.set_parameter(espeak.core.parameter_RATE,self.settings["speed"])
        espeak.synth("")
        self.readyTimer = QtCore.QTimer()
        self.readyTimer.timeout.connect(lambda: self.ready())
        self.readyTimer.start(500)
        
    def ready(self):
        if self.stack != None:
            self.readyTimer.stop()
            window = QtGui.QX11EmbedContainer(self.stack)
            window.resize(700, 480)
            window.embedClient(int(self.wid, 16))
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            bus.add_signal_receiver(self.signal_handler,
                        bus_name='org.navit_project.navit',
                        interface_keyword='interface',
                        member_keyword='member',
                        path_keyword='path',
                        message_keyword='msg')

        
    def signal_handler(self, *args, **kwargs):
        print(args)
        if args[0]:
            self.speech(args[0]["data"])
            self.lastSpeech = args[0]["data"]
    
    def speech(self, text):
        self.parent.pa.lowerVolume("navit")
        espeak.synth(text)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.checkSpeech())
        self.timer.start(1000)
    
    def checkSpeech(self):
        if espeak.is_playing() == False:
            self.timer.stop()
            self.parent.pa.riseVolume()
    
