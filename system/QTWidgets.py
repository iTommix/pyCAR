from PyQt4.QtCore import Qt, QTimeLine, QRect
from PyQt4 import QtCore
from PyQt4.QtGui import *

class FaderWidget(QWidget):
    
    def __init__(self, old_widget, new_widget):
    
        QWidget.__init__(self, new_widget)
        
        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0
        
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(333)
        self.timeline.start()
        
        self.resize(new_widget.size())
        self.show()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        try:
            painter.setOpacity(self.pixmap_opacity)
        except:
            painter.setOpacity(1.0)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()
    
    def animate(self, value):
    
        self.pixmap_opacity = 1.0 - value
        self.repaint()

class QTWidgets(object):

    class QTLabel(QLabel):
        
        def __init__(self, *args):
            QLabel.__init__(self, *args)
            
        def paintEvent( self, event ):
            painter = QPainter(self)
    
            metrics = QFontMetrics(self.font())
            elided  = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
            painter.drawText(self.rect(), self.alignment(), elided)
            
    class StackedWidget(QStackedWidget):

        def __init__(self, parent = None):
            QStackedWidget.__init__(self, parent)
            self.setStyleSheet("border: 0px")
            self.setGeometry(QRect(0, 0, 700, 480))
        
        def setCurrentIndex(self, index):
            self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
            QStackedWidget.setCurrentIndex(self, index)
                

    