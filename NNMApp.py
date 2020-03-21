import asyncio
import sys
from concurrent.futures import FIRST_COMPLETED

from PySide2.QtCore import QSettings, QPoint, QSize, QAbstractListModel, Qt, QTimer
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QSplitter, QListView, QWidget, QScrollArea, \
    QGridLayout

from nnmclub.parser import get_forums, get_topics
from nnmclub.widgets import TopicView

APP_TITLE = "NoNaMe Club"

FAVICON_ICO = "images/favicon.ico"


class ForumModel(QAbstractListModel):
    forums = list()

    def columnCount(self, parent=None):
        return 0

    def data(self, index, role=None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return "{}".format(self.forums[index.row()].name)
        return None

    def rowCount(self, parent=None):
        return len(self.forums)

    def add(self, forum):
        self.beginResetModel()
        self.forums.append(forum)
        self.endResetModel()

    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    forum_model = ForumModel()

    def __init__(self):
        QMainWindow.__init__(self)
        self.ioloop = asyncio.get_event_loop()
        icon = QIcon()
        icon.addPixmap(QPixmap(FAVICON_ICO), QIcon.Normal)
        self.setWindowIcon(icon)
        self.setWindowTitle(APP_TITLE)

        self.settings = QSettings('karoStudio', 'nnm-stats')
        self.resize(self.settings.value('main/size', QSize(640, 480)))
        self.move(self.settings.value('main/pos', QPoint(200, 200)))

        self.splitter = QSplitter()
        self.forum_view = QListView()
        self.forum_view.setStyleSheet("QListView{font: bold 12px;}")
        self.forum_view.clicked.connect(self.listViewClick)
        self.forum_view.setModel(self.forum_model)
        self.splitter.addWidget(self.forum_view)

        self.content = QScrollArea()
        self.torrents_list_view = QWidget()
        layout = QGridLayout()
        self.torrents_list_view.setLayout(layout)
        self.content.setWidget(self.torrents_list_view)
        self.splitter.addWidget(self.content)
        self.splitter.setSizes([200, 400])
        self.setCentralWidget(self.splitter)

        self.timer = QTimer()
        self.timer.singleShot(1000, self.load_task)

    def load_task(self):
        self.ioloop.run_until_complete(self.load_forums())

    async def load_forums(self):
        tasks = [asyncio.ensure_future((get_forums("http://nnmclub.to/")))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        forums = done.pop().result()
        for forum in forums:
            self.forum_model.add(forum)

    def load_torrents_task(self, forum):
        self.ioloop.run_until_complete(self.load_torrents(forum))

    async def load_torrents(self, forum):
        tasks = [asyncio.ensure_future((get_topics(forum)))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        cats = done.pop().result()
        l = QGridLayout()
        cats.sort(key=lambda x: x.likes, reverse=True)
        for i, cat in enumerate(cats):
            l.addWidget(TopicView(cat), i, 0)
        self.torrents_list_view = QWidget()
        self.torrents_list_view.setLayout(l)
        self.content.setWidget(self.torrents_list_view)

    def listViewClick(self, index):
        forum = self.forum_model.forums[index.row()]
        self.setWindowTitle("{} / {}".format(APP_TITLE, forum.name))
        self.timer.singleShot(1000, lambda: self.load_torrents_task(forum))

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
