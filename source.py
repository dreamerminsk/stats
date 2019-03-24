import sqlite3
from typing import Optional, Dict, Any

from PySide2.QtCore import QThread
from PySide2.QtSql import QSqlDatabase, QSqlQuery

_db = sqlite3.connect('video.db', detect_types=sqlite3.PARSE_DECLTYPES)
_db.row_factory = sqlite3.Row


def insert_category(category):
    try:
        _db.execute('insert into categories(id, title) values(?, ?)', (category['id'], category['title'],))
        _db.commit()
    except Exception as ex:
        print(ex)


def get_forums():
    try:
        rows = _db.execute('select * from forums;')
        return rows.fetchall()
    except Exception as ex:
        print(ex)


def get_users():
    try:
        rows = _db.execute('select * from users;')
        return rows.fetchall()
    except Exception as ex:
        print(ex)


def insert_user(u):
    try:
        _db.execute('insert into users values(?, ?, ?, ?)', (u['id'], u['name'], u['registered'], u['nation'],))
        _db.commit()
    except Exception as ex:
        print(ex)


def get_torrent():
    try:
        rows = _db.execute('select * from torrents where last_checked is null order by id desc limit 1')
        return rows.fetchone()
    except Exception as ex:
        print(ex)


def get_check_torrent():
    try:
        rows = _db.execute('select * from torrents_next_checking limit 1')
        return rows.fetchone()
    except Exception as ex:
        print(ex)


def update_torrent(t):
    try:
        _db.execute('''update torrents set title=?,forum=?,hash=?,seed=?,leech=?,downloads=?,
            published=?, last_modified=?, last_checked=?, user_id=? where id=?''',
                    (t['title'], t['forum'], t['hash'], t['seed'], t['leech'], t['downloads'],
                     t['published'], t['last_modified'], t['last_checked'], t['user_id'], t['id'],))
        _db.commit()
    except Exception as ex:
        print(ex)


class DataSource:

    @staticmethod
    def get_db():
        name = "db-" + str(QThread.currentThread())
        if QSqlDatabase.contains(name):
            return QSqlDatabase.database(name)
        else:
            db = QSqlDatabase.addDatabase("QSQLITE", name)
            db.setDatabaseName("video.db")
            return db

    def get_forum_to_scan(self):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(query="select * from forums_to_scan_2 limit 1;", db=db)
            forum = {}
            while query.next():
                forum['id'] = query.value(0)
                forum['title'] = query.value(3)
                forum['delta'] = query.value('delta')
            return forum
        except Exception as ex:
            print(str(ex))
        finally:
            db.close()

    def get_category(self, id):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(db=db)
            query.prepare("select * from categories where id=:id;")
            query.bindValue(':id', id)
            query.exec_()
            category: Dict[str, Optional[Any]] = {}
            while query.next():
                category['id'] = query.value('id')
                category['title'] = query.value('title')
            return category
        finally:
            db.close()

    def get_forum(self, id):
        db = self.get_db()
        try:
            if not db.isOpen():
                db.open()
            query = QSqlQuery(db=db)
            query.prepare("select * from forums where id=:id;")
            query.bindValue(':id', id)
            query.exec_()
            forum: Dict[str, Optional[Any]] = {}
            while query.next():
                forum['id'] = query.value('id')
                forum['category'] = query.value('category')
                forum['title'] = query.value('title')
            return forum
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
                'update torrents set forum=:f, title=:t, seed=:seed, leech=:leech, published=:pub, last_modified=:lm, '
                'hash=:hash, downloads=:d, last_checked=:lc, user_id=:user where id=:id')
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
