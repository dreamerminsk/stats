import asyncio
import sys

import requests
from PySide2.QtCore import QSettings, QPoint, QSize
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QSplitter, QListWidget
from bs4 import BeautifulSoup


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

        ioloop = asyncio.get_event_loop()
        tasks = [ioloop.create_task(self.coro("http://nnmclub.to/"))]
        wait_tasks = asyncio.wait(tasks)
        ioloop.run_until_complete(wait_tasks)
        ioloop.close()

    def load(self):
        print("LOADED")

    async def coro(self, ref):
        urls = []
        s = requests.Session()
        try:
            r = s.get(ref, timeout=24)
            d = BeautifulSoup(r.text, 'html.parser')
            tables = d.select("td.leftnav > table.pline")
            for href in tables[1].select("td.row1 a.genmed"):
                urls.append(href.text)
                print(href.text)
            return urls
        except Exception as exc:
            print(exc)
            return None

    def closeEvent(self, event):
        self.settings.setValue('main/size', self.size())
        self.settings.setValue('main/pos', self.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
