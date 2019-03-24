import sys
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

import requests
from PySide2.QtCore import QTimer, Signal, Slot, Qt, QModelIndex, QAbstractTableModel, QThread, QAbstractItemModel
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QListWidget, QSplitter, QTableView
from PySide2.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from bs4 import BeautifulSoup

import rutracker
import utils
from source import DataSource
from workers import RssWorker


class TorrentParser:
    @staticmethod
    def get_title(doc):
        title = None
        t = doc.select_one('h1.maintitle')
        if t:
            title = t.text.strip()
        return title

    @staticmethod
    def get_forum(doc):
        forum = None
        for item in doc.select('table.w100 a'):
            q = urlparse(item.get('href')).query
            ps = parse_qs(q)
            if 'f' in ps:
                forum = ps['f'][0]
        return forum

    @staticmethod
    def get_seed(doc):
        seed = 0
        seed_item = doc.select_one('.seed b')
        if seed_item:
            seed = int(seed_item.text.strip())
        return seed

    @staticmethod
    def get_leech(doc):
        leech = 0
        leech_item = doc.select_one('.leech b')
        if leech_item:
            leech = int(leech_item.text.strip())
        return leech

    @staticmethod
    def get_published(doc):
        published = None
        pi = doc.select_one('p.post-time a')
        if pi:
            published = utils.parse_date(pi.text.strip())
        return published

    @staticmethod
    def get_last_modified(doc):
        lm = None
        lmi = doc.select_one('.posted_since')
        if lmi:
            idx = lmi.text.find('ред. ')
            if idx > 0:
                val = lmi.text[idx + 5:idx + 20]
                lm = utils.parse_date(val)
        return lm

    @staticmethod
    def get_hash(doc):
        tor_hash = None
        hi = doc.select_one('#tor-tor_hash')
        if hi:
            tor_hash = hi.text.strip()
        return tor_hash

    @staticmethod
    def get_downloads(doc):
        downloads = 0
        for n in doc.select('li'):
            if n.text.startswith('Скачан'):
                downloads = utils.extract_int(n.text)
        return downloads

    @staticmethod
    def get_user(doc):
        user = 0
        for n in doc.select('a'):
            if n.text.startswith('[Профиль]'):
                q = urlparse(n.get('href')).query
                ps = parse_qs(q)
                if 'u' in ps:
                    user = ps['u'][0]
        return user

    def parse(self, doc):
        topic = dict()
        topic['forum'] = self.get_forum(doc)
        topic['title'] = self.get_title(doc)
        topic['seed'] = self.get_seed(doc)
        topic['leech'] = self.get_leech(doc)
        topic['published'] = self.get_published(doc)
        topic['last_modified'] = self.get_last_modified(doc)
        topic['hash'] = self.get_hash(doc)
        topic['downloads'] = self.get_downloads(doc)
        topic['last_checked'] = datetime.now()
        topic['user_id'] = self.get_user(doc)
        return topic


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
        self.timer.start(4368)
        self.torrents = 0

    def process(self):
        t = self.ds.get_torrent()
        print(t)
        if 'id' not in t:
            return
        doc, error = rutracker.get_topic(t['id'])
        if error is not None:
            print(error)
            return
        parser = TorrentParser()
        topic = parser.parse(doc)
        topic['id'] = t['id']
        self.ds.insert_torrent(topic)
        self.torrents += 1
        self.newtorrents.emit(self.torrents)
        row = self.t.rowCount()
        self.t.setRowCount(row + 1)
        self.t.setItem(row, 0, QTableWidgetItem(str(datetime.now())))
        self.t.setItem(row, 1, QTableWidgetItem(str(topic['downloads'])))
        self.t.setItem(row, 2, QTableWidgetItem(str(topic['title'])))
        self.t.setItem(row, 3, QTableWidgetItem(str(topic['published'])))
        self.listmodel.addItem(str(topic['published'])[:10])


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
        doc, error = rutracker.get_topic(t['id'])
        if error is not None:
            print(error)
            return
        parser = TorrentParser()
        topic = parser.parse(doc)
        topic['id'] = t['id']
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


class RssCategoryItem:

    def __init__(self, category, forums, topics):
        self.category = category
        self.forums = forums
        self.topics = topics


class RssCategoryModel(QAbstractItemModel):
    cats: Dict[Any, Any]

    def canFetchMore(self, parent):
        return False

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            catname = ''
            for i, key in enumerate(self.cats.keys()):
                if i == index.row():
                    catname = key
            if index.column() == 0:
                return self.cats[catname].category
            elif index.column() == 1:
                return self.cats[catname].forums
            elif index.column() == 2:
                return self.cats[catname].topics
            else:
                return None
        return None

    def fetchMore(self, parent):
        pass

    def hasChildren(self, parent=None, *args, **kwargs):
        pass

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole & orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def index(self, row, column, parent=None, *args, **kwargs):
        if not parent.isValid():
            catname = ''
            for i, key in enumerate(self.cats.keys()):
                if i == row:
                    catname = key
            return self.createIndex(row, column, self.cats[catname])
        return QModelIndex()

    def insertRow(self, row, parent=None, *args, **kwargs):
        pass

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        pass

    def itemData(self, index):
        return {}

    def parent(self, child):
        return QModelIndex()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.cats)

    def setData(self, index, value, role=None):
        return False

    def setItemData(self, index, roles):
        return False

    def sort(self, column, order=None):
        pass

    def addCategory(self, category, torrents):
        if category in self.cats:
            self.beginResetModel()
            self.cats[category].forums += 1
            self.cats[category].topics += torrents
            self.endResetModel()
        else:
            self.beginInsertRows(QModelIndex(), len(self.cats), len(self.cats))
            item = RssCategoryItem(category, 1, torrents)
            self.cats[category] = item
            self.endInsertRows()

    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.headers = ['Category', 'Forums', 'Topics']
        self.categories = []
        self.cats = dict()


class RssWidget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.cat_table = QTableView(self)
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
        print(forum)
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
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
