from PySide2.QtCore import QObject, QAbstractItemModel, Qt, QModelIndex
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTreeView

from source import DataSource


class CategoryItem(QObject):
    pass


class ForumItem(QObject):
    pass


class ForumModel(QAbstractItemModel):

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, index, role=None):
        return None

    def headerData(self, section, orientation, role=None):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return 'Title'
        else:
            return None

    def index(self, row, column, parent=None, *args, **kwargs):
        return QModelIndex()

    def itemData(self, index):  # real signature unknown; restored from __doc__
        """ itemData(self, index: PySide2.QtCore.QModelIndex) -> typing.Dict """
        pass

    def parent(self):
        return QModelIndex()

    def rowCount(self, parent=None, *args, **kwargs):  # real signature unknown; NOTE: unreliably restored from __doc__
        return 1

    def __init__(self, *args, **kwargs):
        QAbstractItemModel.__init__(self)
        self.ds = DataSource()

class LeftMenuWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.tree = QTreeView(self)
        self.tree.setSortingEnabled(True)
        self.tree.setModel(ForumModel())
        self.splitter.addWidget(self.tree)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
