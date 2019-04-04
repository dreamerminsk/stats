from PySide2.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTreeView

from source import DataSource


class LeftMenuWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.tree = QTreeView(self)
        self.tree.setSortingEnabled(True)
        # self.treemodel = NewTorrentModel()
        # self.list.setModel(self.listmodel)
        self.splitter.addWidget(self.tree)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.ds = DataSource()
