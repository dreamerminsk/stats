import sys
from datetime import datetime

import requests
from PySide2.QtCore import QTimer, Signal, Slot, Qt, QModelIndex, QAbstractTableModel, QThread, QAbstractItemModel
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QListWidget, QSplitter, QTableView, \
    QTreeView
from PySide2.QtWidgets import QStyleFactory
from PySide2.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from bs4 import BeautifulSoup

import rutracker
from source import DataSource
from workers import RssWorker


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


class RssRootCategoryItem:

    def __init__(self) -> object:
        self.categories = []
        self.is_last_changed = False

    def addChild(self, child):
        self.categories.append(child)

    def child(self, index):
        return self.categories[index]

    def childCount(self):
        return len(self.categories)

    def data(self, index):
        if index == 0:
            return 'Категории'
        elif index == 1:
            forums = 0
            for item in self.categories:
                forums += item.forums
            return forums
        elif index == 2:
            topics = 0
            for item in self.categories:
                topics += item.topics
            return topics
        else:
            return None

    def parent(self):
        return None

    def row(self):
        return 0


class RssCategoryItem:

    def __init__(self, parentItem, category, forums, topics):
        self.parentItem = parentItem
        self.category = category
        self.forums = forums
        self.topics = topics
        self.is_last_changed = False

    def child(self, index):
        return None

    def childCount(self):
        return 0

    def data(self, index):
        if index == 0:
            return self.category
        elif index == 1:
            return self.forums
        elif index == 2:
            return self.topics
        else:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        return self.parentItem.categories.index(self)


class RssCategoryModel2(QAbstractItemModel):
    rssroot: RssRootCategoryItem

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def data(self, index, role=None):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.ForegroundRole:
            if item.is_last_changed:
                return QColor(Qt.blue)
            else:
                return QColor(Qt.black)
        elif role == Qt.FontRole:
            font = QApplication.font()
            if item.is_last_changed:
                font.setBold(True)
                return font
            else:
                font.setBold(False)
                return font

        return None

    def hasChildren(self, parent=None):
        if self.rowCount(parent) > 0:
            return True
        else:
            return False

    def headerData(self, section, orientation, role=None):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headers[section]
        else:
            return None

    def index(self, row, column, parent=None):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self.rssroot)
        else:
            parentItem = parent.internalPointer()
            childItem: object = parentItem.child(row)
            if childItem:
                return self.createIndex(row, column, childItem)
            else:
                return QModelIndex();
        return QModelIndex()

    def insertRow(self, row, parent=None, *args, **kwargs):
        pass

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        pass

    def itemData(self, index):
        return {}

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()
        childItem = child.internalPointer()
        parentItem = childItem.parent()
        if (parentItem == None):
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem);

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return 1
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount();

    def setData(self, index, value, role=None):
        return False

    def setItemData(self, index, roles):
        return False

    def addCategory(self, category, torrents):
        if self.last_changed_items[0]:
            self.last_changed_items[0].is_last_changed = False
            parentTopLeft = self.index(0, 0, QModelIndex())
            childTopLeft = self.index(self.last_changed_items[0].row(), 0, parentTopLeft)
            childBottomRight = self.index(self.last_changed_items[0].row(), 0, parentTopLeft)
            self.dataChanged.emit(childTopLeft, childBottomRight)
        self.last_changed_items[0] = self.last_changed_items[1]
        self.last_changed_items[1] = self.last_changed_items[2]
        cat = None
        for item in self.rssroot.categories:
            if item.category == category:
                cat = item
        if cat:
            cat.forums += 1
            cat.topics += torrents
            cat.is_last_changed = True
            self.last_changed_items[2] = cat
            parentTopLeft = self.index(0, 0, QModelIndex())
            parentBottomRight = self.index(0, 2, QModelIndex())
            childTopLeft = self.index(cat.row(), 0, parentTopLeft)
            childBottomRight = self.index(cat.row(), 0, parentTopLeft)
            self.dataChanged.emit(parentTopLeft, parentBottomRight)
            self.dataChanged.emit(childTopLeft, childBottomRight)
        else:
            self.beginInsertRows(QModelIndex(), self.rssroot.childCount(), self.rssroot.childCount())
            item = RssCategoryItem(self.rssroot, category, 1, torrents)
            item.is_last_changed = True
            self.last_changed_items[2] = item
            self.rssroot.addChild(item)
            self.endInsertRows()

    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.headers = ['Category', 'Forums', 'Topics']
        self.rssroot = RssRootCategoryItem()
        self.last_changed = None
        self.last_changed_items = [None, None, None]


class RssWidget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.cat_table = QTreeView(self)
        self.cat_model = RssCategoryModel2()
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
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
