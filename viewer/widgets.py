from PySide2.QtCore import QObject, QAbstractItemModel, Qt, QModelIndex
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTreeView

from source import DataSource


class CategoryItem(QObject):

    def __init__(self, parent, cat) -> object:
        self.parent_item = parent
        self.cat = cat
        self.forums = []

    def child(self, index):
        return self.forums[index]

    def childCount(self):
        return len(self.forums)

    def data(self, index):
        if index == 0:
            return self.cat['title']
        else:
            return None

    def parent(self):
        return None

    def row(self):
        return self.parent_item.find(self)

    def find(self, item):
        return self.forums.index(item)


class ForumItem(QObject):
    def __init__(self, parent, forum) -> object:
        self.parent_item = parent
        self.forum = forum
        self.forums = []

    def child(self, index):
        return self.forums[index]

    def childCount(self):
        return len(self.forums)

    def data(self, index):
        if index == 0:
            return self.forum['title']
        else:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        return self.parent_item.find(self)

    def find(self, item):
        return self.forums.index(item)


class ForumModel(QAbstractItemModel):

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, index, role=None):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        return None

    def headerData(self, section, orientation, role=None):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return 'Title'
        else:
            return None

    def index(self, row, column, parent=None, *args, **kwargs):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self.categories[row])
        else:
            parentItem = parent.internalPointer()
            childItem: object = parentItem.child(row)
            if childItem:
                return self.createIndex(row, column, childItem)
            else:
                return QModelIndex()
        return QModelIndex()

    def itemData(self, index):
        return {}

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()
        childItem = child.internalPointer()
        parentItem = childItem.parent()
        if (parentItem == None):
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.categories)
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def find(self, item):
        return self.categories.index(item)

    def __init__(self, *args, **kwargs):
        QAbstractItemModel.__init__(self)
        self.ds = DataSource()
        self.cats = self.ds.get_categories()
        self.categories = []
        for cat in self.cats:
            self.categories.append(CategoryItem(self, cat))

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
