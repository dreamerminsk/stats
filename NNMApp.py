import asyncio
import sys
from concurrent.futures import FIRST_COMPLETED

from PySide2.QtCore import QSettings, QPoint, QSize, QAbstractListModel, Qt, QTimer
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QSplitter, QListView, QWidget, QScrollArea, \
    QGridLayout, QLabel

from nnmclub.parser import get_forums, get_torrents


class CatModel(QAbstractListModel):
    cats = list()

    def columnCount(self, parent=None):
        return 0

    def data(self, index, role=None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return "{}".format(self.cats[index.row()].name)
        return None

    def rowCount(self, parent=None):
        return len(self.cats)

    def add(self, cat):
        self.beginResetModel()
        self.cats.append(cat)
        self.endResetModel()

    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    cat_model = CatModel()

    def __init__(self):
        QMainWindow.__init__(self)
        self.ioloop = asyncio.get_event_loop()
        icon = QIcon()
        icon.addPixmap(QPixmap("images/favicon.ico"), QIcon.Normal)
        self.setWindowIcon(icon)
        self.setWindowTitle("NoNaMe Club")

        self.settings = QSettings('karoStudio', 'nnm-stats')
        self.resize(self.settings.value('main/size', QSize(640, 480)))
        self.move(self.settings.value('main/pos', QPoint(200, 200)))

        self.splitter = QSplitter()
        self.cat_view = QListView()
        self.cat_view.setStyleSheet("QListView{font: bold 12px;}")
        self.cat_view.clicked.connect(self.listViewClick)
        self.cat_view.setModel(self.cat_model)
        self.splitter.addWidget(self.cat_view)

        self.content = QScrollArea()
        self.torrents_list_view = QWidget()
        layout = QGridLayout()
        for i in range(100):
            layout.addWidget(QLabel("TORRENT {}".format(i)), i, 0)
        self.torrents_list_view.setLayout(layout)
        self.content.setWidget(self.torrents_list_view)
        self.splitter.addWidget(self.content)
        self.setCentralWidget(self.splitter)

        self.timer = QTimer()
        self.timer.singleShot(1000, self.load_task)

    def load_task(self):
        self.ioloop.run_until_complete(self.load_forums())

    async def load_forums(self):
        tasks = [asyncio.ensure_future((get_forums("http://nnmclub.to/")))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        cats = done.pop().result()
        for cat in cats:
            self.cat_model.add(cat)

    def load_torrents_task(self, forum):
        self.ioloop.run_until_complete(self.load_torrents(forum))

    async def load_torrents(self, forum):
        tasks = [asyncio.ensure_future((get_torrents(forum)))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        cats = done.pop().result()
        l = QGridLayout()
        for i, cat in enumerate(cats):
            print(cat)
            l.addWidget(QLabel("{}".format(cat.name)), i, 0)
        self.torrents_list_view = QWidget()
        self.torrents_list_view.setLayout(l)
        self.content.setWidget(self.torrents_list_view)

    def listViewClick(self, index):
        cat = self.cat_model.cats[index.row()]
        self.setWindowTitle("NoNaMe Club / " + cat.name)
        self.timer.singleShot(1000, lambda: self.load_torrents_task(cat))

    def closeEvent(self, event):
        self.settings.setValue('main/size', self.size())
        self.settings.setValue('main/pos', self.pos())
        self.ioloop.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
