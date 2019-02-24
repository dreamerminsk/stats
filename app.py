
import sqlite3


_db = sqlite3.connect('video.db', detect_types=sqlite3.PARSE_DECLTYPES)
_db.row_factory = sqlite3.Row

_mdb = sqlite3.connect('../music/releases.db', detect_types=sqlite3.PARSE_DECLTYPES)
_mdb.row_factory = sqlite3.Row

_bdb = sqlite3.connect('../books/books.db', detect_types=sqlite3.PARSE_DECLTYPES)
_bdb.row_factory = sqlite3.Row

def insert(sql, params):
    try:
        print(params)
        _db.execute(sql, params)
        _db.commit()
    except Exception as e:
        print(e)


r = _mdb.execute('select * from torrents')
for i in r:
    insert('insert into torrents (id,forum,title,seed,leech,published,last_modified,hash,downloads,last_checked) values(?,?,?,?,?,?,?,?,?,?)', (i['id'], i['forum'], i['title'],i['seed'],i['leech'],i['published'],i['last_modified'],i['hash'],i['downloads'],i['last_checked'],))