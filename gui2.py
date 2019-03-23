import sys
from datetime import datetime

from PySide2.QtCore import QThread, QTimer
from PySide2.QtCore import Signal
from PySide2.QtSql import QSqlDatabase, QSqlQuery
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout

import rutracker


class TorrentsWidget(QWidget):
    newtorrents = Signal(int)

    def __init__(self):
        QWidget.__init__(self)
        l = QVBoxLayout(self)
        self.t = QTableWidget(0, 4, self)
        l.addWidget(self.t)
        self.setLayout(l)
        self.ds = DataSource()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        self.timer.start(4368)
        self.torrents = 0

    def process(self):
        t = self.ds.get_torrent()
        print(t)
        if 'id' not in t:
            return
        doc, error = rutracker.get_topic(t['id'])
        if error is not None:
            print(error)
            return
        parser = TorrentParser()
        topic = parser.parse(doc)
        topic['id'] = t['id']
        self.ds.insert_torrent(topic)
        self.torrents += 1
        self.newtorrents.emit(self.torrents)
        row = self.t.rowCount()
        self.t.setRowCount(row + 1)
        self.t.setItem(row, 0, QTableWidgetItem(str(datetime.now())))
        self.t.setItem(row, 1, QTableWidgetItem(str(topic['downloads'])))
        self.t.setItem(row, 2, QTableWidgetItem(str(topic['title'])))
        self.t.setItem(row, 3, QTableWidgetItem(str(topic['published'])))


class DataSource():

    def get_db(self):
        name = "db-" + str(QThread.currentThread())
        if QSqlDatabase.contains(name):
            return QSqlDatabase.database(name)
        else:
            db = QSqlDatabase.addDatabase("QSQLITE", name)
            db.setDatabaseName("video.db")
            return db

    def get_categories(self):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            cs = list()
            query = QSqlQuery(query="select * from categories;", db=db)
            forum = {}
            while query.next():
                c = {}
                c['id'] = query.value(0)
                c['title'] = query.value(1)
                cs.append(c)
            return cs
        except Exception as ex:
            print(str(ex))
        finally:
            db.close()

    def get_torrent(self):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(query="select * from torrents where last_checked is null order by id desc limit 1;",
                              db=db)
            topic = {}
            while query.next():
                topic['id'] = query.value('id')
                topic['forum'] = query.value('forum')
                topic['title'] = query.value('title')
                topic['seed'] = query.value('seed')
                topic['leech'] = query.value('leech')
                topic['published'] = query.value('published')
                topic['last_modified'] = query.value('last_modified')
                topic['hash'] = query.value('hash')
                topic['downloads'] = query.value('downloads')
                topic['last_checked'] = query.value('last_checked')
                topic['user_id'] = query.value('user_id')
            return topic
        finally:
            db.close()

    def get_check_torrent(self):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(query="select * from torrents_next_checking limit 1;", db=db)
            topic = {}
            while query.next():
                topic['id'] = query.value('id')
                topic['forum'] = query.value('forum')
                topic['title'] = query.value('title')
                topic['seed'] = query.value('seed')
                topic['leech'] = query.value('leech')
                topic['published'] = query.value('published')
                topic['last_modified'] = query.value('last_modified')
                topic['hash'] = query.value('hash')
                topic['downloads'] = query.value('downloads')
                topic['last_checked'] = query.value('last_checked')
                topic['user_id'] = query.value('user_id')
            return topic
        finally:
            db.close()

    def save_torrent(self, torrent):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(db=db)
            query.prepare('insert into torrents(id, forum, title) values(:id, :f, :t)')
            query.bindValue(':id', torrent[0])
            query.bindValue(':f', torrent[1])
            query.bindValue(':t', torrent[2])
            return query.exec_()
        except Exception as ex:
            return False
        finally:
            db.close()

    def insert_torrent(self, torrent):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(db=db)
            query.prepare(
                'update torrents set forum=:f, title=:t, seed=:seed, leech=:leech, published=:pub, last_modified=:lm, hash=:hash, downloads=:d, last_checked=:lc, user_id=:user where id=:id')
            query.bindValue(':id', torrent['id'])
            query.bindValue(':f', torrent['forum'])
            query.bindValue(':t', torrent['title'])
            query.bindValue(':seed', torrent['seed'])
            query.bindValue(':leech', torrent['leech'])
            query.bindValue(':pub', str(torrent['published']))
            query.bindValue(':lm', str(torrent['last_modified']))
            query.bindValue(':hash', torrent['hash'])
            query.bindValue(':d', torrent['downloads'])
            query.bindValue(':lc', str(torrent['last_checked']))
            query.bindValue(':user', torrent['user_id'])
            return query.exec_()
        except Exception as ex:
            return False
        finally:
            db.close()

    def update_rss(self, f, d, ls):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(db=db)
            query.prepare('update forums_rss set last_scanned=:ls, delta=:d where id=:id')
            query.bindValue(':ls', str(ls))
            query.bindValue(':d', d)
            query.bindValue(':id', f)
            query.exec_()
            db.close()
            return True
        except Exception as ex:
            return False
        finally:
            db.close()


class MyWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("RuTracker.org")
        self.setGeometry(200, 200, 640, 480)
        self.tree = QTreeWidget(self)
        self.setCentralWidget(self.tree)
        self.ds = DataSource()
        cs = self.ds.get_categories()
        for c in cs:
            i = QTreeWidgetItem(self.tree)
            i.setText(0, c['title'])
            self.tree.addTopLevelItem(i)

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    label = MyWindow()
    label.show()
    sys.exit(app.exec_())
