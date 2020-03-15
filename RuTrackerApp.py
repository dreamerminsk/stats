import sys

from PySide2.QtCore import QSettings, QPoint, QSize, Qt
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QVBoxLayout, QLabel, QScrollArea

from source import DataSource


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.settings = QSettings('karoStudio', 'rt-stats')
        self.resize(self.settings.value('main/size', QSize(640, 480)))
        self.move(self.settings.value('main/pos', QPoint(200, 200)))
        self.ds = DataSource()
        cats = self.ds.get_categories()
        self.layout = QVBoxLayout()
        self.content = QScrollArea()
        self.content.setLayout(self.layout)
        for cat in cats:
            lbl = QLabel(cat['title'])
            self.layout.addWidget(lbl, 1, Qt.AlignTop)
        self.setCentralWidget(self.content)

    def closeEvent(self, event):
        self.settings.setValue('main/size', self.size())
        self.settings.setValue('main/pos', self.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
