import sys

from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QStyleFactory

from source import DataSource
from viewer.widgets import LeftMenuWidget


class MyWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("RuTracker.org")
        self.setGeometry(200, 200, 640, 480)
        self.tree = LeftMenuWidget()
        self.setCentralWidget(self.tree)
        self.ds = DataSource()

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
