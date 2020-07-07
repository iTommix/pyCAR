
import subprocess, time, os, sys
from PyQt4 import QtCore, QtGui, uic

path=os.path.dirname(os.path.abspath( __file__ ))
form_class = uic.loadUiType(path+"/gui.ui")[0]

class navit(QtGui.QMainWindow, form_class):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent=parent
        self.setupUi(self)
        self.stack = None
        process = subprocess.Popen(['navit', '-c', '/usr/local/share/navit/navit.xml'],stdout=subprocess.PIPE, shell=True)
        pid = str(process.pid)
        cmd='xwininfo -name \'Navit\' | sed -e \'s/^ *//\' | grep -E "Window id" | awk \'{ print $4 }\''
        wid='';
        while wid=="" :
            proc = subprocess.check_output(cmd, shell=True)
            wid=proc.decode("utf-8").replace("\n","");
    
        self.readyTimer = QtCore.QTimer()
        self.readyTimer.timeout.connect(lambda: self.ready(wid))
        self.readyTimer.start(500)

        
    def ready(self, wid):
        if self.stack != None:
            self.readyTimer.stop()
            window = QtGui.QX11EmbedContainer(self.stack)
            window.resize(700, 480)
            window.embedClient(int(wid, 16))
            
        
    def focus(self):
        pass
    
    def mute(self):
        pass
            
    def playing(self):
        return 0



def main():
    app = QtGui.QApplication(sys.argv)
    form = navit()
    form.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()