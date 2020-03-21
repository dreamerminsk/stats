from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel


class TopicView(QWidget):
    def __init__(self, topic):
        QWidget.__init__(self)
        self.topic = topic
        self.setStyleSheet(
            "QWidget{"
            "border-width: 1px;"
            "border-style: solid;"
            "border-color: darkgrey;"
            "border-radius: 4px;}")
        layout = QGridLayout(self)
        self.title = QLabel(topic.name)
        layout.addWidget(self.title, 0, 0, 1, 4, Qt.AlignLeft)
        self.setLayout(layout)
