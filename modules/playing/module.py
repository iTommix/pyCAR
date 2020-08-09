#from PyQt4 import QtGui, uic
from PyQt5 import QtWidgets
import os, time

class playing(QtWidgets.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)
        
    def loaded(self):
        pass
    
    def focus(self):
        self.parent.mainFrame.setCurrentIndex(self.parent.modules[self.parent.player]["deck"])
