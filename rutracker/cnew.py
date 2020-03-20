import sqlite3
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

db = sqlite3.connect('video.db', detect_types=sqlite3.PARSE_DECLTYPES)
db.row_factory = sqlite3.Row
c = db.cursor()

ids = db.execute('select id from categories')
cs = []
for id in ids:
    cs.append(id[0])
url = 'https://rutracker.org/'
while url:
    r = requests.get(url)
    doc = BeautifulSoup(r.text, 'html.parser')
    for link in doc.select('a'):
        q = urlparse(link.get('href')).query
        ps = parse_qs(q)
        if 'c' in ps:
            if int(ps['c'][0]) not in cs:
                print(link.text)
        url = None

ids = db.execute('select id from forums')
fs = []
for id in ids:
    fs.append(id[0])
for cat in db.execute('select * from categories'):
    print('-------------------------')
    print(cat['title'])
    r = requests.get('https://rutracker.org/forum/index.php?c=' + str(cat['id']))
    doc = BeautifulSoup(r.text, 'html.parser')
    for link in doc.select('a'):
        q = urlparse(link.get('href')).query
        ps = parse_qs(q)
        if 'f' in ps:
            if int(ps['f'][0]) not in fs:
                print(ps['f'][0], link.text)
                db.execute(
                    'insert into forums(id, title, subscribed, last_updated, last_scanned_page) values(?, ?, 1, '
                    'datetime("now", "-1 year"), 1)',
                    (ps['f'][0], link.text.strip(),))
                db.commit()
                db.execute(
                    'insert into forums_rss(id, delta, last_scanned) values(?, 3600, datetime("now", "-1 year"))',
                    (ps['f'][0],))
                db.commit()
                # fs.remove(ps['f'][0])

db.close()
