import sqlite3


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

