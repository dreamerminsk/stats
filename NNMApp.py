import asyncio
import sys
from concurrent.futures import FIRST_COMPLETED

import requests
from PySide2.QtCore import QSettings, QPoint, QSize, QAbstractListModel, Qt, QTimer
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QSplitter, QListView
from bs4 import BeautifulSoup

from nnmclub.models import Category


class CatModel(QAbstractListModel):
    cats = list()

    def columnCount(self, parent=None):
        return 0

    def data(self, index, role=None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return "{} - {}".format(self.cats[index.row()].id, self.cats[index.row()].name)
        return None

    def rowCount(self, parent=None):
        return len(self.cats)

    def add(self, cat):
        self.beginResetModel()
        self.cats.append(cat)
        self.endResetModel()

    def __init__(self):
        super().__init__()


async def get_cats(ref):
    urls = []
    s = requests.Session()
    try:
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("td.leftnav > table.pline")
        for href in tables[1].select("td.row1 a.genmed"):
            urls.append(Category.parse(href))
        return urls
    except Exception as exc:
        print(exc)
        return None


class MainWindow(QMainWindow):
    cat_model = CatModel()

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
        self.cat_view = QListView()
        self.cat_view.setModel(self.cat_model)
        self.splitter.addWidget(self.cat_view)
        self.setCentralWidget(self.splitter)

        self.timer = QTimer()
        self.timer.singleShot(0, self.load_task)

    def load_task(self):
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(self.load())
        ioloop.close()

    async def load(self):
        tasks = [asyncio.ensure_future((get_cats("http://nnmclub.to/")))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        cats = done.pop().result()
        for cat in cats:
            self.cat_model.add(cat)

    def closeEvent(self, event):
        self.settings.setValue('main/size', self.size())
        self.settings.setValue('main/pos', self.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
