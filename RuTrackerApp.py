import sys

from PySide2.QtCore import QSettings, QPoint, QSize, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QScrollArea, QGridLayout, \
    QWidget, QPushButton

from source import DataSource


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.settings = QSettings('karoStudio', 'rt-stats')
        self.resize(self.settings.value('main/size', QSize(640, 480)))
        self.move(self.settings.value('main/pos', QPoint(200, 200)))
        self.ds = DataSource()
        cats = self.ds.get_categories()
        self.layout = QGridLayout()
        list_cats = QWidget()
        list_cats.setLayout(self.layout)
        self.content = QScrollArea()
        for row, cat in enumerate(cats):
            lbl = QPushButton(cat['title'])
            lbl.setFont(QFont(pointSize=70))
            self.layout.addWidget(lbl, row, 0, Qt.AlignTop)
        self.content.setViewport(list_cats)
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
