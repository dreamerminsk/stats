import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import sqlite3
import time
import datetime
import random


db=sqlite3.connect('video.db', detect_types=sqlite3.PARSE_DECLTYPES)
c=db.cursor()


def update(id, f, title):
    try:
        t = db.execute('select * from torrents where id=?', (id,)).fetchone()
        if (t[1] != f) or (t[2] != title):
            db.execute('update torrents set forum=?, title=? where id=?',(f, title, id,))
            db.commit()
            print('  [update]: ' + str(t))
            print('  [update]: ' + str((id, f, title,)))
    except Exception as ex:
        print('\t' + ex.__class__.__name__ + ':' + str(ex))



def store(id, f, title):
    try:
        db.execute('insert into torrents(id, forum, title) values(?,?,?)',(id, f, title))
        db.commit()
        print('  [insert]: ' + str((id, f, title,)))
    except sqlite3.IntegrityError as iex:
        update(id, f, title)
    except Exception as ex:
        print('\t' + ex.__class__.__name__ + ':' + str(ex))

before = db.execute('select count(id) from torrents').fetchone()[0]
cur=db.execute('''select id, title, last_updated,
 julianday()-julianday(last_updated, "utc")
 +7*(random()/9223372036854775808) as diff, last_scanned_page
 from forums where subscribed=1 order by diff desc limit 16''')
forums = cur.fetchall()
forum = forums[0]
for f in forums:
    print(f)
    url='https://rutracker.org/forum/viewforum.php?f=' + str(f[0])
    if f[4] > 1:
        url += '&start=' + str(50*(f[4]-1))
    print('==========')
    print(f)
    cp=f[4]
    tp=0
    start = datetime.datetime.now()
    while url:
        print('----')
        finish = datetime.datetime.now()
        after = db.execute('select count(id) from torrents').fetchone()[0]
        print('elapsed: ' + str(finish-start) + ' /' + str(after-before)+ '/')
        remaining = (tp-cp)*(finish-start)/cp
        print('remaining: ' + str(remaining))
        print('total: ' + str(finish-start+remaining))
        print('average: ' + str((finish-start)/cp))
        print(str(cp) + ' of ' + str(tp) + '> ' + url)
        cp+=1
        time.sleep(1+random.randint(0, 3))
        r=requests.get(url)
        print('  length=' + str(len(r.text)))
        doc=BeautifulSoup(r.text, 'html.parser')
        url=''
        for pg in doc.select('a.pg'):
            if pg.text == 'След.':
                url='https://rutracker.org/forum/' + pg.get('href')
            elif pg.text == 'Пред.':
                pass
            else:
                p=int(pg.text)
                if p>tp:
                    tp=p
        for link in doc.select('a.torTopic'):
            q=urlparse(link.get('href')).query
            ps=parse_qs(q)
            if 't' in ps:
                if '201' in link.text:
                    print(ps['t'], ' ', link.text)
                    store(ps['t'][0], f[0], link.text)
                if '2009' in link.text:
                    print(ps['t'], ' ', link.text)
                    store(ps['t'][0], f[0], link.text)
        db.execute('update forums set last_scanned_page=? where id=?', (cp-1, f[0],))
        db.commit()
    db.execute('update forums set last_updated=datetime("now", "localtime"), last_scanned_page=1 where id=?', (f[0],))
    db.commit()

    for item in c.execute('select * from forums where id=?', (f[0],)):
        print(item)

for item in c.execute('select count(id) from torrents'):
    print('>>>', item[0], '(', (item[0]-before),')')

db.close()

end = datetime.datetime.now()
print(str(end-start))
