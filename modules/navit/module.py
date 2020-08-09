import dbus
from dbus.mainloop.glib import DBusGMainLoop
import subprocess, time, os, sys, signal
#from PyQt4 import QtCore, QtGui, uic
from PyQt5.QtGui import QWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon, QPixmap
from espeak import espeak

path=os.path.dirname(os.path.abspath( __file__ ))



class navit(QtWidgets.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.stack = None
        self.lastSpeech = None
        process = subprocess.Popen(['navit'],stdout=subprocess.PIPE, shell=True)
        self.pid = process.pid+1
        cmd='xwininfo -name \'Navit\' | sed -e \'s/^ *//\' | grep -E "Window id" | awk \'{ print $4 }\''
        self.wid='';
        while self.wid=="" :
            proc = subprocess.check_output(cmd, shell=True)
            self.wid=proc.decode("utf-8").replace("\n","");
        
    def unload(self):
        os.kill(self.pid, signal.SIGINT)
        
    def focus(self):
        if self.lastSpeech != None:
            self.speech(self.lastSpeech)
    

    def loaded(self):
        espeak.set_voice(self.settings["voice"])
        espeak.set_parameter(espeak.core.parameter_RATE,self.settings["speed"])
        espeak.synth("")
        window = QWindow.fromWinId(int(self.wid, 16))
        window.resize(700, 480)
        widget = QtWidgets.QWidget.createWindowContainer(window)
        self.stack.addWidget(widget)
        
        font = QtGui.QFont('SansSerif', 15, QtGui.QFont.Bold)
        self.anouncement = QtWidgets.QWidget(self.parent)
        self.anouncement.setGeometry(QtCore.QRect(110, -10, 680, 100))
        self.anouncement.setStyleSheet("background-color: #eee; border-radius: 10px; border: 1px solid #000")
        self.label=QtWidgets.QLabel(self.anouncement)
        self.label.setGeometry(QtCore.QRect(110, 10, 570, 80))
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background-image: none; border: 0px; border-radius: 0px; background: transparent;")
        self.image = QtWidgets.QLabel(self.anouncement)
        self.image.setGeometry(QtCore.QRect(0, 10, 100, 100))
        self.image.setStyleSheet("background-image: none; border: 0px; border-radius: 0px; background: transparent;")
        pixmap = QPixmap('/usr/share/navit/icons/nav_left_1_bk_96_96.png')
        self.image.setPixmap(pixmap)
        self.anouncement.hide()
        self.fade(self.anouncement)
        
        
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus.add_signal_receiver(self.signal_handler,
                    bus_name='org.navit_project.navit',
                    interface_keyword='interface',
                    member_keyword='member',
                    path_keyword='path',
                    message_keyword='msg')

        
    def signal_handler(self, *args, **kwargs):
        if args[0]:
            self.speech(args[0]["data"])
            self.lastSpeech = args[0]["data"]
    
    def speech(self, text):
        self.label.setText(text)
        self.unfade(self.anouncement)
        self.parent.pa.lowerVolume("navit")
        espeak.synth(text)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.checkSpeech())
        self.timer.start(1000)
    
    def checkSpeech(self):
        if espeak.is_playing() == False:
            self.timer.stop()
            self.parent.pa.riseVolume()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(lambda: self.hideAnouncement())
            self.timer.start(5000)
            
    def hideAnouncement(self):
        self.timer.stop()
        self.fade(self.anouncement)


    def fade(self, widget):
        self.anouncement.hide()
        self.effect = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)
    
        self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
    
    def unfade(self, widget):
        self.anouncement.show()
        self.effect = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)
    
        self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()