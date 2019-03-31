from PySide2.QtCore import QAbstractItemModel, Qt, QModelIndex
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication


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


class RssCategoryModel(QAbstractItemModel):
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
