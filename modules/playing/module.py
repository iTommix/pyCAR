from PyQt4 import QtGui, uic
import os, time
path=os.path.dirname(os.path.abspath( __file__ ))
form_class = uic.loadUiType(path+"/gui.ui")[0]

class playing(QtGui.QMainWindow, form_class):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        
    def loaded(self):
        pass
    
    def focus(self):
        self.parent.mainFrame.setCurrentIndex(self.parent.modules[self.parent.player]["deck"])
