from PyQt5 import QtWidgets, QtGui


class example(QtWidgets.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)

        
    ############### MANDATORY ! #################
    # This will be called after the module is   #
    # loaded and the GUI is available           #
    #############################################
    def loaded(self):
        self.button1.clicked.connect(lambda: self.goto(1))
        self.button2.clicked.connect(lambda: self.goto(0))
        
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
    #def play(self):

    
    #############################################
    # If your module plays music or similar     #
    # this will be called if another module is  #
    # selected to play its own music            #
    #############################################
    #def stop(self):


    def goto(self, page):
        ########################################
        # Switch to another page               #
        ########################################
        self.parent.setPage(self.stack, page)
        ########################################
        # Display the status on the mainscreen #
        ########################################
        self.parent.setInfo("Module Example", "is on Page "+str(page+1))


def main():
    app = QtGui.QApplication(sys.argv)
    form = example()
    form.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()