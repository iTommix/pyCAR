from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel, QFontMetrics, QPainter

class Label(QLabel):
    def paintEvent( self, event ):
        painter = QPainter(self)

        metrics = QFontMetrics(self.font())
        elided  = metrics.elidedText(self.text(), Qt.ElideRight, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)