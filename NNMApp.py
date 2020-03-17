import sys

from PySide2.QtCore import QSettings, QPoint, QSize
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QLabel, QFrame, QSplitter, QListWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("images/favicon.ico"), QIcon.Normal)
        self.setWindowIcon(icon)
        self.setWindowTitle("NoNaMe Club")

        self.settings = QSettings('karoStudio', 'nnm-stats')
        self.resize(self.settings.value('main/size', QSize(640, 480)))
        self.move(self.settings.value('main/pos', QPoint(200, 200)))

        self.splitter = QSplitter()
        self.splitter.addWidget(QListWidget())
        self.setCentralWidget(self.splitter)

    def createLabel(self, text):
        label = QLabel(text)
        label.setFrameStyle(QFrame.Box | QFrame.Raised)
        return label

    def closeEvent(self, event):
        self.settings.setValue('main/size', self.size())
        self.settings.setValue('main/pos', self.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
