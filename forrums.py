import requests
from bs4 import BeautifulSoup
import sqlite3
import time


def get_forum(index):
    url = 'https://rutracker.org/forum/viewforum.php?f=' + str(index)
    html = requests.get(url)
    doc = BeautifulSoup(html.text, 'html.parser')
    title = ''
    for item in doc.select('.maintitle'):
        title = item.text
    cat = -1
    cat_title = ''
    for item in doc.select('.w100.pad_2 a'):
        href = item.get('href')
        if '?c=' in href:
            cat = href[href.find('?c=')+3:]
            cat_title = item.text.strip()
            print(cat_title)
    return (index, cat, title, 0)


db = sqlite3.connect('releases.db', detect_types=sqlite3.PARSE_DECLTYPES)


def update(forum):
    try:
        db.execute("update forums set category=?, title=? where id=?",
        (forum[1], forum[2], forum[0],))
        db.commit()
        cur = db.execute('select * from forums where id=?', (forum[0],))
        print('  update <', cur.fetchone(), '>')
    except Exception as ex:
        print(ex)



def store(forum):
    try:
        db.execute("insert into forums values (?, ?, ?, ?, datetime('now', 'localtime'))", forum)
        db.commit()
        cur = db.execute('select * from forums where id=?', (forum[0],))
        print('  insert <', cur.fetchone(), '>')
    except sqlite3.IntegrityError:
        update(forum)
    except Exception as ex:
        print(ex)

r= [560,794,793,556,436,969,2307,2308,2309,2310,2311,557,558]
for i in range(2540, 2700):
    forum = get_forum(i)
    if forum[2]:
        print(forum)
        store(forum)
        time.sleep(12)

db.close()
