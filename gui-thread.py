import sys
from datetime import datetime

import requests
from PySide2.QtCore import QTimer, Signal, Slot, Qt, QModelIndex, QAbstractTableModel, QThread
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QListWidget, QSplitter, QTableView, \
    QTreeView
from PySide2.QtWidgets import QStyleFactory
from PySide2.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from bs4 import BeautifulSoup

import rutracker
from model.models import RssCategoryModel, NewTorrentModel
from source import DataSource
from workers import RssWorker, NewTorrentWorker


class NewTorrentLM(QAbstractTableModel):

    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.days = list()
        self.stats = dict()

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self.days[index.row()]
            elif index.column() == 1:
                return str(self.stats[self.days[index.row()]])
            else:
                return None
        else:
            return None

    def headerData(self, section, orientation, role=None):
        pass

    def insertRow(self, row, parent=None, *args, **kwargs):
        pass

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.days)

    def addItem(self, item):
        if self.days.count(str(item)) == 0:
            self.beginInsertRows(QModelIndex(), len(self.days), len(self.days))
            self.days.append(str(item))
            self.stats[str(item)] = 1
            self.days.sort()
            self.endInsertRows()
        else:
            self.beginResetModel()
            self.stats[str(item)] += 1
            self.endResetModel()


class TorrentsWidget(QWidget):
    list: QListWidget
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.list = QTreeView(self)
        self.listmodel = NewTorrentModel()
        self.list.setModel(self.listmodel)
        self.splitter.addWidget(self.list)
        self.t = QTableWidget(0, 4, self)
        self.splitter.addWidget(self.t)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.ds = DataSource()
        self.worker = NewTorrentWorker()
        self.worker_thread = QThread()
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.worker.processed.connect(self.processed)

    def finish(self):
        self.worker.finish()
        self.worker_thread.quit()
        self.worker_thread.wait()

    def processed(self, topic):
        self.listmodel.add_topic(topic['published'])


class Torrents2Widget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.list = QTableView(self)
        self.listmodel = NewTorrentLM()
        self.list.setModel(self.listmodel)
        self.splitter.addWidget(self.list)
        self.t = QTableWidget(0, 4, self)
        self.splitter.addWidget(self.t)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.ds = DataSource()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        self.timer.start(3768)
        self.torrents = 0

    def process(self):
        t = self.ds.get_check_torrent()
        print(t)
        if 'id' not in t:
            return
        topic, error = rutracker.get_topic2(t['id'])
        if error is not None:
            print(error)
            return
        self.ds.insert_torrent(topic)
        self.torrents += 1
        self.newtorrents.emit(self.torrents)
        row = self.t.rowCount()
        self.t.setRowCount(row + 1)
        self.t.setItem(row, 0, QTableWidgetItem(str(datetime.now())))
        self.t.setItem(row, 1, QTableWidgetItem(str(topic['downloads'])))
        self.t.setItem(row, 2, QTableWidgetItem(str(topic['title'])))
        self.t.setItem(row, 3, QTableWidgetItem(str(topic['published'])))
        self.listmodel.addItem(str(topic['published'])[:7])


class RssWidget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.cat_table = QTreeView(self)
        self.cat_model = RssCategoryModel()
        self.cat_table.setModel(self.cat_model)
        self.splitter.addWidget(self.cat_table)
        self.t = QTableWidget(0, 4, self)
        self.splitter.addWidget(self.t)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.ds = DataSource()
        self.worker = RssWorker()
        self.worker_thread = QThread()
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.worker.processed.connect(self.processed)

    @Slot(int, int)
    def processed(self, forum_id, torrents):
        forum = self.ds.get_forum(forum_id)
        cat = self.ds.get_category(forum['category'])
        self.cat_model.addCategory(cat['title'], torrents)

    def finish(self):
        self.worker.finish()
        self.worker_thread.quit()
        self.worker_thread.wait()


class MyWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("RuTracker.org")
        self.setGeometry(200, 200, 640, 480)
        self.tabwidget = QTabWidget()
        self.rsslbl = QLabel("RSS")
        self.rsslist = QListWidget(self)
        self.rss = RssWidget()
        self.tabwidget.addTab(self.rss, "rss")
        self.twidget = TorrentsWidget()
        self.twidget.newtorrents.connect(self.update_tab_1)
        self.tabwidget.addTab(self.twidget, "new torrents")
        self.t2widget = Torrents2Widget()
        self.t2widget.newtorrents.connect(self.update_tab_2)
        self.tabwidget.addTab(self.t2widget, "check torrents")
        self.setCentralWidget(self.tabwidget)
        self.ds = DataSource()

    @Slot(int)
    def update_tab_1(self, torrents):
        self.tabwidget.setTabText(1, 'new torrents /' + str(torrents) + '/')

    @Slot(int)
    def update_tab_2(self, torrents):
        self.tabwidget.setTabText(2, 'check torrents /' + str(torrents) + '/')

    @staticmethod
    def get_page(ref):
        try:
            r = requests.get(ref, timeout=24)
            doc = BeautifulSoup(r.text, 'html.parser')
            return doc, None
        except Exception as ex:
            return None, ex

    def get_rss(self, forum):
        ref = 'http://feed.rutracker.cc/atom/f/' + str(forum['id']) + '.atom'
        (doc, error) = self.get_page(ref)
        return doc, error

    def closeEvent(self, event):
        self.rss.finish()
        self.twidget.finish()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
