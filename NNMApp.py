import asyncio
import sys
from concurrent.futures import FIRST_COMPLETED

from PySide2.QtCore import QSettings, QPoint, QSize, QAbstractListModel, Qt, QTimer
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QStyleFactory, QMainWindow, QSplitter, QListView, QWidget, QScrollArea, \
    QGridLayout

from nnmclub.models import Forum
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
    forum = Forum(id=-1, name="UNKNOWN")
    topics = []
    forum_model = ForumModel()

    def __init__(self):
        QMainWindow.__init__(self)
        self.date_view = QListView()
        self.forum_view = QListView()
        self.contentMax = 0
        self.ioloop = asyncio.get_event_loop()
        icon = QIcon()
        icon.addPixmap(QPixmap(FAVICON_ICO), QIcon.Normal)
        self.setWindowIcon(icon)
        self.setWindowTitle(APP_TITLE)

        self.settings = QSettings('karoStudio', 'nnm-stats')
        self.resize(self.settings.value('main/size', QSize(640, 480)))
        self.move(self.settings.value('main/pos', QPoint(200, 200)))

        self.splitter = QSplitter()
        self.get_menu()

        self.content = QScrollArea()
        self.content.verticalScrollBar().valueChanged.connect(self.scrollBarChanged)
        self.content.verticalScrollBar().rangeChanged.connect(self.rangeChanged)
        self.torrents_list_view = QWidget()
        layout = QGridLayout()
        self.torrents_list_view.setLayout(layout)
        self.content.setWidget(self.torrents_list_view)
        self.splitter.addWidget(self.content)
        self.splitter.setSizes([160, 350])
        self.setCentralWidget(self.splitter)

        self.timer = QTimer()
        self.timer.singleShot(1600, self.load_task)

    def get_menu(self):
        scroll = QScrollArea(self)
        self.forum_view.setStyleSheet("QListView{font: bold 12px;}")
        self.forum_view.clicked.connect(self.listViewClick)
        self.forum_view.setModel(self.forum_model)

        menu_splitter = QSplitter(self)
        menu_splitter.setOrientation(Qt.Vertical)
        menu_splitter.addWidget(self.forum_view)
        menu_splitter.addWidget(self.date_view)
        scroll.setWidget(menu_splitter)
        scroll.adjustSize()
        self.splitter.addWidget(scroll)

    def load_task(self):
        self.ioloop.run_until_complete(self.load_forums())

    async def load_forums(self):
        tasks = [asyncio.ensure_future((get_forums("http://nnmclub.to/")))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        forums = done.pop().result()
        for forum in forums:
            print(forum)
            self.forum_model.add(forum)

    def load_torrents_task(self, forum, start):
        self.ioloop.run_until_complete(self.load_torrents(forum, start))

    async def load_torrents(self, forum, start=0):
        tasks = [asyncio.ensure_future((get_topics(forum, start)))]
        done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        if start == 0:
            self.topics = done.pop().result()
        else:
            self.topics = self.topics + done.pop().result()
        layout = QGridLayout()
        self.topics.sort(key=lambda x: x.likes, reverse=True)
        for i, topic in enumerate(self.topics):
            print("{}. {}".format(i, topic))
            layout.addWidget(TopicView(topic), i, 0)
        self.torrents_list_view = QWidget()
        self.torrents_list_view.setLayout(layout)
        self.content.setWidget(self.torrents_list_view)

    def rangeChanged(self, vert_min, vert_max):
        self.contentMax = vert_max

    def scrollBarChanged(self, value):
        if value == self.contentMax:
            print("LOADING {}".format(self.torrents_list_view.children()))
            self.timer.singleShot(1000, lambda: self.load_torrents_task(self.forum, len(self.topics)))

    def listViewClick(self, index):
        self.forum = self.forum_model.forums[index.row()]
        self.topics = []
        self.setWindowTitle("{} / {}".format(APP_TITLE, self.forum.name))
        # self.timer.singleShot(1000, lambda: self.load_torrents_task(self.forum, 0))
        self.timer.timeout.connect(lambda: self.load_torrents_task(self.forum, len(self.topics)))
        self.timer.start(8000)

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
