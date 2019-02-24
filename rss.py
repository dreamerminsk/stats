import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import sqlite3
import time
import timestring
from datetime import datetime, timedelta


def get_page(ref):
    try:
        r = requests.get(ref, timeout=24)
        doc = BeautifulSoup(r.text, 'html.parser')
        return (doc, None)
    except Exception as ex:
        return (None, ex)


def getRss(forum):
    print('----')
    print(forum['title'])
    print('\tlast scanned: ' + str(forum['last_scanned']))
    print('\ttimedelta: ' + str(timedelta(seconds=forum['delta'])))
    ref = 'http://feed.rutracker.cc/atom/f/' + str(forum['id']) + '.atom'
    (doc, error) = get_page(ref)
    return doc, error

db = sqlite3.connect('video.db', detect_types=sqlite3.PARSE_DECLTYPES)
db.row_factory = sqlite3.Row

def getTorrentCount():
    count = 0
    try:
        c = db.execute('select count(id) from torrents')
        count = c.fetchone()[0]
    except Exception as ex:
        print('[getTorrentCount]: ' + ex)
    finally:
        c.close()
    return count


def update_torrent(torrent):
    try:
        db.execute('update torrents set forum=? where id=?', (torrent[1], torrent[0],))
        print('  [update]: ' + str(torrent))
        db.commit()
    except Exception as ex:
        pass


def saveTorrent(torrent):
    try:
        db.execute('insert into torrents(id, forum, title) values(?, ?, ?)', torrent)
        print('  [insert]: ' + str(torrent))
        db.commit()
    except sqlite3.IntegrityError as iex:
        pass
    except Exception as ex:
        pass


def update_rss(f, d, ls):
    try:
        db.execute('update forums_rss set last_scanned=?, delta=? where id=?', (ls, d, f,))
        db.commit()
    except Exception as ex:
        print(ex)


start = datetime.now()
startcount = getTorrentCount()

db.execute('insert into rss_updates(start, finish, inserted) values(?, ?, ?)', (start, start, 0,))
db.commit()

while True:
    cursor = db.execute('''select * from forums_to_scan_2 limit 1''')
    forum = cursor.fetchone()
    if forum is None:
        break
    print(forum['next_scanning'], forum['title'])
    time.sleep(1)
    doc, error = getRss(forum)
    if error is not None:
        print(error)
        continue
    currentcount = getTorrentCount()

    for entry in doc.find_all('entry'):
        url = entry.find('link')
        q = urlparse(url.get('href')).query
        ps = parse_qs(q)
        torrent = (ps['t'][0], forum['id'], entry.find('title').text,)
#        if ('2018' in torrent[2]) or ('2017' in torrent[2]) or ('2016' in torrent[2]) or ('2015' in torrent[2]):
        saveTorrent(torrent)

    finish = datetime.now()
    finishcount = getTorrentCount()
    if (finishcount-currentcount) > 0:
        update_rss(forum['id'], forum['delta']*0.9, finish)
    else:
        update_rss(forum['id'], forum['delta']*1.1, finish)
    print()
    print('inserted: ' + str(finishcount-startcount))
    print('time: ' + str(finish-start))
    db.execute('update rss_updates set finish=?, inserted=? where start=?', (finish, finishcount-startcount, start,))
    db.commit()

finish = datetime.now()
finishcount = getTorrentCount()
print()
print('==================')
print('inserted: ' + str(finishcount-startcount))
print('time: ' + str(finish-start))

db.execute('update rss_updates set finish=?, inserted=? where start=?', (finish, finishcount-startcount, start,))
db.commit()

cursor = db.execute('''select * from forums_to_scan''')
forums = cursor.fetchall()
print('next scan:')

for forum in forums:
    print(forum['title'])
    print('\t', forum['next_scanning'], str(timedelta(seconds=forum['delta'])))

db.close()
