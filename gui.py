import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests
from PySide2.QtCore import QTimer, Signal, Slot, Qt, QModelIndex, QAbstractTableModel
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QListWidget, QSplitter, QTableView
from PySide2.QtWidgets import QStyleFactory
from PySide2.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from bs4 import BeautifulSoup

import rutracker
import utils
from source import DataSource


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
        print(pi)
        if pi:
            published = utils.parse_date(pi.text.strip())
            print(pi.text.strip())
            print(published)
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
        else:
            hi = doc.select_one('#tor-hash')
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
        if self.get_title(doc) is None:
            print('TITLE: ' + doc.select_one('title').text)
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
        self.timer.start(16000)
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
        self.timer.start(12000)
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
        self.listmodel.addItem(str(topic['published'])[:4])


class MyWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("RuTracker.org")
        self.setGeometry(200, 200, 640, 480)
        self.tabwidget = QTabWidget()
        self.rsslbl = QLabel("RSS")
        self.rsslist = QListWidget(self)
        self.rsstable = QTableWidget(self)
        self.rsstable.setColumnCount(5)
        self.rsstable.setRowCount(0)
        self.tabwidget.addTab(self.rsstable, "get_forum_to_scan")
        self.twidget = TorrentsWidget()
        self.twidget.newtorrents.connect(self.update_tab_1)
        self.tabwidget.addTab(self.twidget, "new torrents")
        self.t2widget = Torrents2Widget()
        self.t2widget.newtorrents.connect(self.update_tab_2)
        self.tabwidget.addTab(self.t2widget, "check torrents")
        self.setCentralWidget(self.tabwidget)
        self.counter = 0
        self.rss_total = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        self.timer.start(8000)
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

    def process(self):
        print('get_forum_to_scan')
        self.counter += 1
        torrents = 0
        f = self.ds.get_forum_to_scan()
        if 'id' not in f:
            # self.rsslist.addItem(str(datetime.now()))
            # self.rsslist.scrollToBottom()
            return
        doc, error = self.get_rss(f)
        if error is not None:
            print(error)
        for entry in doc.find_all('entry'):
            url = entry.find('link')
            q = urlparse(url.get('href')).query
            ps = parse_qs(q)
            torrent = (ps['t'][0], f['id'], entry.find('title').text,)
            print('RSS: ' + str(torrent))
            # self.rsslist.addItem('\t' + torrent[2])
            if self.ds.save_torrent(torrent):
                torrents += 1
        # self.rsslist.scrollToBottom()
        delta = f['delta']
        if torrents > 0:
            self.rss_total += torrents
            delta = delta * 0.9
            self.ds.update_rss(f['id'], delta, datetime.now())
        else:
            delta = delta * 1.1
            self.ds.update_rss(f['id'], delta, datetime.now())
        row = self.rsstable.rowCount()
        self.rsstable.setRowCount(row + 1)
        self.rsstable.setItem(row, 0, QTableWidgetItem(str(datetime.now())))
        self.rsstable.setItem(row, 1, QTableWidgetItem(str(f['id'])))
        self.rsstable.setItem(row, 2, QTableWidgetItem(f['title']))
        self.rsstable.setItem(row, 3, QTableWidgetItem(str(torrents)))
        self.rsstable.setItem(row, 4, QTableWidgetItem(str(delta)))
        self.tabwidget.setTabText(0, 'get_forum_to_scan /' + str(self.rsstable.rowCount()) + ', ' + str(self.rss_total) + '/')

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    label = MyWindow()
    label.show()
    sys.exit(app.exec_())
