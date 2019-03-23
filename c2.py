import sqlite3
import time

import rutracker

db = sqlite3.connect('video.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = db.cursor()


def update(id, f, title):
    try:
        t = db.execute('select * from torrents where id=?', (id,)).fetchone()
        if (t[1] != f) or (t[2] != title):
            db.execute('update torrents set forum=?, title=? where id=?', (f, title, id,))
            db.commit()
            print('  [update]: ' + str(t))
            print('  [update]: ' + str((id, f, title,)))
    except Exception as ex:
        print('\t' + ex.__class__.__name__ + ':' + str(ex))


def update2(id, cat, parent, title):
    try:
        t = db.execute('select * from forums where id=?', (id,)).fetchone()
        if (t[1] != cat) or (t[2] != parent) or (t[3] != title):
            db.execute(
                'update forums set category=?, parent=?, title=?, last_updated=datetime("now", "localtime") where id=?',
                (cat, parent, title, id,))
            db.commit()
            print('  [update]: ' + str(t))
            print('  [update]: ' + str((id, cat, parent, title,)))
    except Exception as ex:
        print('\t' + ex.__class__.__name__ + ':' + str(ex))


def update3(id, cat, title):
    try:
        t = db.execute('select * from forums where id=?', (id,)).fetchone()
        if (t[1] != cat) or (t[3] != title):
            db.execute('update forums set category=?, title=?, last_updated=datetime("now", "localtime") where id=?',
                       (cat, title, id,))
            db.commit()
            print('  [update]: ' + str(t))
            print('  [update]: ' + str((id, cat, title,)))
    except Exception as ex:
        print('\t' + ex.__class__.__name__ + ':' + str(ex))


def store(id, f, title):
    try:
        db.execute('insert into torrents(id, forum, title) values(?,?,?)', (id, f, title))
        db.commit()
        print('  [insert]: ' + str((id, f, title,)))
    except sqlite3.IntegrityError as iex:
        update(id, f, title)
    except Exception as ex:
        print('\t' + ex.__class__.__name__ + ':' + str(ex))


cur = db.execute('''select * from forums where category is null;''')
forums = cur.fetchall()
for f in forums:
    doc = None
    while doc == None:
        print(f)
        doc, ex = rutracker.get_forum(f[0])
    nav = []
    navt = []
    for p in doc.select('.nav.nav-top > a'):
        print(p['href'])
        navt.append(p.text)
        nav.append(p['href'])
    if len(nav) < 3:
        continue
    print(navt)
    print(nav)
    print(nav[1][12:], '/', nav[1], '/', navt[1])
    print(nav[len(nav) - 2][16:], '/', nav[len(nav) - 2], '/', navt[len(nav) - 2])
    print(nav[len(nav) - 1][16:], '/', nav[len(nav) - 1], '/', navt[len(nav) - 1])
    if len(nav) > 3:
        update2(f[0], int(nav[1][12:]), int(nav[len(nav) - 2][16:]), navt[len(nav) - 1].strip())
    if len(nav) == 3:
        update3(f[0], int(nav[1][12:]), navt[len(nav) - 1].strip())
    time.sleep(8)

db.close()
