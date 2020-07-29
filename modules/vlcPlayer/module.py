import sys
import vlc
from PyQt4 import QtGui, uic



class vlcPlayer(QtGui.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtGui.QWidget.__init__(self, parent)
        #self.loaded()
        
    ############### MANDATORY ! #################
    # This will be called after the module is   #
    # loaded and the GUI is available           #
    #############################################
    def loaded(self):
        #uic.loadUi("./gui.ui", self)
        self.vlc_instance = vlc.Instance()
        self.mediaplayer = self.vlc_instance.media_player_new()
        self.mediaplayer.set_xwindow(int(self.page1.winId()))
        self.media_path = "rtp://87.141.215.251@232.0.10.111:10000"
        self.media = self.vlc_instance.media_new(self.media_path)
        self.media.get_mrl()
        self.mediaplayer.set_media(self.media)
        
        
    #############################################
    # This will be called if the button on the  #
    # mainscreen is pressed and the module got  #
    # the focus                                 #
    #############################################  
    def focus(self):
        self.parent.setInfo("Module Example", "is on Page "+str(self.stack.currentIndex()+1))
    
    #############################################
    # If your module plays music or similar     #
    # this will be called if the button on the  #
    # mainscreen is pressed or another module   #
    # force a 'resume' like the phone module    #
    #############################################
    def play(self):
        self.mediaplayer.play()
    
    #############################################
    # If your module plays music or similar     #
    # this will be called if another module is  #
    # selected to play its own music            #
    #############################################
    def stop(self):
        self.mediaplayer.stop()


    def goto(self, page):
        ########################################
        # Switch to another page               #
        ########################################
        self.stack.setCurrentIndex(page)
        ########################################
        # Display the status on the mainscreen #
        ########################################
        self.parent.setInfo("Module Example", "is on Page "+str(page+1))


def main():
    app = QtGui.QApplication(sys.argv)
    form = vlcPlayer()
    form.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()