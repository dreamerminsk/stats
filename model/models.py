﻿from datetime import datetime

from PySide2.QtCore import QAbstractItemModel, Qt, QModelIndex, QObject
from dateutil.parser import parse


class RssRootCategoryItem:

    def __init__(self) -> object:
        self.categories = []

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
        return None

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
            parent_item = parent.internalPointer()
            child_item: object = parent_item.child(row)
            if child_item:
                return self.createIndex(row, column, child_item)
            else:
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
        child_item = child.internalPointer()
        parent_item = child_item.parent()
        if (parent_item == None):
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item);

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return 1
        else:
            parent_item = parent.internalPointer()
        return parent_item.childCount()

    def addCategory(self, category, torrents):
        cat = None
        for item in self.rssroot.categories:
            if item.category == category:
                cat = item
        if cat:
            cat.forums += 1
            cat.topics += torrents
            parentTopLeft = self.index(0, 0, QModelIndex())
            parentBottomRight = self.index(0, 2, QModelIndex())
            childTopLeft = self.index(cat.row(), 0, parentTopLeft)
            childBottomRight = self.index(cat.row(), 2, parentBottomRight)
            self.dataChanged.emit(parentTopLeft, parentBottomRight)
            self.dataChanged.emit(childTopLeft, childBottomRight)
        else:
            self.beginInsertRows(self.index(0, 0, QModelIndex()), self.rssroot.childCount(), self.rssroot.childCount())
            it = RssCategoryItem(self.rssroot, category, 1, torrents)
            self.rssroot.addChild(it)
            self.endInsertRows()

    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.headers = ['Category', 'Forums', 'Topics']
        self.rssroot = RssRootCategoryItem()


class PublishedNewTorrent(QObject):

    def __init__(self) -> object:
        super().__init__()
        self.none = NoneNewTorrent(self)
        self.years = []

    def append(self, child):
        self.years.append(child)

    def addChild(self, child) -> object:
        queue = []
        if child is None:
            return queue
        for y in self.years:
            if y.year == child.year:
                queue.extend(y.addChild(child))
                return queue
        new_node = YearNewTorrent(self, child.year)
        queue.append((self, new_node))
        queue.extend(new_node.addChild(child))
        return queue

    def child(self, index):
        if index == 0:
            return self.none
        return self.years[index - 1]

    def childCount(self):
        return len(self.years) + 1

    def data(self, index):
        if index == 0:
            return 'Published'
        elif index == 1:
            return self.topics
        else:
            return None

    def parent(self):
        return None

    def row(self):
        return 0

    @property
    def topics(self):
        topics = self.none.topics
        for item in self.years:
            topics += item.topics
        return topics

    def find(self, published: datetime):
        print('TOPIC FIND: ' + str(type(published)) + '| ' + str(published))
        if published is None:
            return self.none
        if published == 'None':
            return self.none
        for year in self.years:
            if year.year == published.year:
                return year.find(published)
        return None


class YearNewTorrent(QObject):

    def __init__(self, parent, year) -> object:
        self.parent_item = parent
        self.year = year
        self.months = []

    def append(self, child: object):
        self.months.append(child)

    def addChild(self, child):
        queue = []
        for m in self.months:
            if m.month == child.month:
                queue.extend(m.addChild(child))
                return queue
        new_node = MonthNewTorrent(self, child.year, child.month)
        queue.append((self, new_node))
        queue.extend(new_node.addChild(child))
        return queue

    def child(self, index):
        return self.months[index]

    def childCount(self):
        return len(self.months)

    def data(self, index):
        if index == 0:
            return str(self.year)
        elif index == 1:
            return self.topics
        else:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        return self.parent_item.years.index(self) + 1

    @property
    def topics(self):
        topics = 0
        for item in self.months:
            topics += item.topics
        return topics

    def find(self, published: datetime):
        for m in self.months:
            if m.month == published.month:
                return m.find(published)
        return None


class MonthNewTorrent(QObject):

    def __init__(self, parent, year, month) -> object:
        self.parent_item = parent
        self.year = year
        self.month = month
        self.days = []

    def append(self, child):
        self.days.append(child)

    def addChild(self, child):
        queue = []
        for d in self.days:
            if d.day == child.day:
                return queue
        new_node = DayNewTorrent(self, child.year, child.month, child.day)
        queue.append((self, new_node))
        return queue

    def child(self, index):
        return self.days[index]

    def childCount(self):
        return len(self.days)

    def data(self, index):
        if index == 0:
            return str(self.year) + '-' + '{:02}'.format(self.month)
        elif index == 1:
            return self.topics
        else:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        return self.parent_item.months.index(self)

    @property
    def topics(self):
        topics = 0
        for item in self.days:
            topics += item.topics
        return topics

    def find(self, published: datetime):
        for d in self.days:
            if d.day == published.day:
                return d
        return None


class DayNewTorrent(QObject):

    def __init__(self, parent, year, month, day) -> object:
        self.parent_item = parent
        self.year = year
        self.month = month
        self.day = day
        self.topics = 1

    def child(self, index):
        return None

    def childCount(self):
        return 0

    def data(self, index):
        if index == 0:
            return str(self.year) + '-' + '{:02}'.format(self.month) + '-' + '{:02}'.format(self.day)
        elif index == 1:
            return self.topics
        else:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        return self.parent_item.days.index(self)


class NoneNewTorrent(QObject):

    def __init__(self, parent) -> object:
        self.parent_item = parent
        self.topics = 0

    def child(self, index):
        return None

    def childCount(self):
        return 0

    def data(self, index):
        if index == 0:
            return 'None'
        elif index == 1:
            return self.topics
        else:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        return 0


class NewTorrentModel(QAbstractItemModel):

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def data(self, index, role=None):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
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
            return self.createIndex(row, column, self.root)
        else:
            parentItem = parent.internalPointer()
            childItem: object = parentItem.child(row)
            if childItem:
                return self.createIndex(row, column, childItem)
            else:
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
        if parentItem is None:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return 1
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def setData(self, index, value, role=None):
        return False

    def setItemData(self, index, roles):
        return False

    def add_topic(self, published):
        if type(published) == str:
            published = parse(published)
        print('\t\t\tADD_TOPIC: ' + str(published))
        p = self.root.find(published)
        print('\t\t\tADD_TOPIC: ' + str(p))
        if p:
            p.topics += 1
            self.dataChanged.emit(self.createIndex(p.row(), 0, p), self.createIndex(p.row(), 1, p))
            self.update_path(p)
        else:
            queue = self.root.addChild(published)
            for item in queue:
                self.beginInsertRows(self.createIndex(item[0].row(), 0, item[0]), item[0].childCount(),
                                     item[0].childCount())
                item[0].append(item[1])
                self.endInsertRows()

    def update_path(self, p):
        cur = p
        while cur.parent() is not None:
            self.dataChanged.emit(self.createIndex(cur.row(), 0, cur), self.createIndex(cur.row(), 1, cur))
            cur = cur.parent()

    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.headers = ['Published', 'Topics']
        self.root = PublishedNewTorrent()
