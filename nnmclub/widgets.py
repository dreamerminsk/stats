from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout


class TopicView(QWidget):
    def __init__(self, topic):
        QWidget.__init__(self)
        self.topic = topic
        layout = QGridLayout(self)

        self.title = QLabel(topic.name)
        self.title.setStyleSheet(
            "QLabel{"
            "border-width: 1px;"
            "border-style: solid;"
            "border-color: darkgrey;"
            "border-radius: 4px;}")
        self.title.setStyleSheet("QLabel{font-size: 14px}")
        layout.addWidget(self.title, 0, 0, 1, 4, Qt.AlignLeading)

        self.like_box = QHBoxLayout(self)
        self.like_icon = QLabel()
        self.like_icon.setPixmap(QPixmap("images\\thanks_on.png"))
        self.likes = QLabel("{} likes".format(topic.likes))
        self.likes.setStyleSheet("QLabel{font-size: 14px;}")
        self.like_box.addWidget(self.like_icon)
        self.like_box.addWidget(self.likes)
        layout.addLayout(self.like_box, 1, 0, 1, 4, Qt.AlignLeading)
        self.setLayout(layout)
