import sys

from PySide2.QtCore import Signal, Slot, QThread, QSettings, QSize, QPoint, \
    QSortFilterProxyModel
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QListWidget, QSplitter, QTreeView
from PySide2.QtWidgets import QStyleFactory
from PySide2.QtWidgets import QWidget, QTableWidget, QVBoxLayout

from model.models import RssCategoryModel, NewTorrentModel
from source import DataSource
from workers import RssWorker, NewTorrentWorker, UpdateTorrentWorker, UpdateUserWorker


class TorrentsWidget(QWidget):
    list: QListWidget
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.list = QTreeView(self)
        self.list.setSortingEnabled(True)
        self.model = NewTorrentModel()
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(self.model)
        self.list.setModel(proxy)
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
        self.model.add_topic(topic['published'])


class Torrents2Widget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.list = QTreeView(self)
        self.list.setSortingEnabled(True)
        self.model = NewTorrentModel()
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(self.model)
        self.list.setModel(proxy)
        self.splitter.addWidget(self.list)
        self.t = QTableWidget(0, 4, self)
        self.splitter.addWidget(self.t)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.ds = DataSource()
        self.worker = UpdateTorrentWorker()
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
        self.model.add_topic(topic['published'])


class RssWidget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.cats = QTreeView(self)
        self.cats.setSortingEnabled(True)
        self.cat_model = RssCategoryModel()
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(self.cat_model)
        self.cats.setModel(proxy)
        self.splitter.addWidget(self.cats)
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
        print('\t\t\tRSS: ' + str(forum_id) + ', ' + str(torrents))
        forum = self.ds.get_forum(forum_id)
        print('\t\t\tRSS FORUM: ' + str(forum))
        cat = self.ds.get_category(forum['category'])
        print('\t\t\tRSS CAT: ' + str(cat))
        self.cat_model.addCategory(cat['title'], torrents)

    def finish(self):
        self.worker.finish()
        self.worker_thread.quit()
        self.worker_thread.wait()


class UserWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.ds = DataSource()
        self.worker = UpdateUserWorker()
        self.worker_thread = QThread()
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.worker.processed.connect(self.processed)

    @Slot(int, int)
    def processed(self, user):
        print('\t\t\tUSER: ' + str(user['id']) + ', ' + str(user['name']) + ', ' + str(user['registered']) + ', ' + str(
            user['nation']))

    def finish(self):
        self.worker.finish()
        self.worker_thread.quit()
        self.worker_thread.wait()


class MyWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        settings = QSettings('dreamix Studio', 'rt-stats')
        self.setWindowTitle("RuTracker.org")
        self.setGeometry(200, 200, 640, 480)
        self.tabwidget = QTabWidget()

        self.rsslbl = QLabel("RSS")
        self.rsslist = QListWidget(self)
        self.rss = RssWidget()
        self.rss.splitter.restoreState(settings.value('main/rss/splitter'))
        self.tabwidget.addTab(self.rss, "rss")

        self.twidget = TorrentsWidget()
        self.twidget.splitter.restoreState(settings.value('main/new/splitter'))
        self.twidget.list.header().restoreState(settings.value('main/new/tree'))
        self.tabwidget.addTab(self.twidget, "new torrents")

        self.t2widget = Torrents2Widget()
        self.t2widget.splitter.restoreState(settings.value('main/update/splitter'))
        self.tabwidget.addTab(self.t2widget, "check torrents")
        self.setCentralWidget(self.tabwidget)

        self.userwidget = UserWidget()
        self.tabwidget.addTab(self.userwidget, "users")
        self.setCentralWidget(self.tabwidget)

        self.ds = DataSource()
        self.resize(settings.value('main/size', QSize(640, 480)))
        self.move(settings.value('main/pos', QPoint(200, 200)))

    def closeEvent(self, event):
        self.rss.finish()
        self.twidget.finish()
        self.t2widget.finish()
        settings = QSettings('dreamix Studio', 'rt-stats')
        settings.setValue('main/size', self.size())
        settings.setValue('main/pos', self.pos())
        settings.setValue('main/rss/splitter', self.rss.splitter.saveState())
        settings.setValue('main/new/splitter', self.twidget.splitter.saveState())
        settings.setValue('main/new/tree', self.twidget.list.header().saveState())
        settings.setValue('main/update/splitter', self.t2widget.splitter.saveState())
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
