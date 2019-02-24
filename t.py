import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import rutracker
import utils
import source
import datetime
import time
import random
import math


def get_title(doc):
    title = None
    t = doc.select_one('h1.maintitle')
    if t:
        title = t.text.strip()
    return title

def get_forum(doc):
    forum = None
    for item in doc.select('table.w100 a'):
        q = urlparse(item.get('href')).query
        ps = parse_qs(q)
        if 'f' in ps:
            forum = ps['f'][0]
    return forum


def get_seed(doc):
    seed = 0
    seed_item= doc.select_one('.seed b')
    if seed_item:
        seed = int(seed_item.text.strip())
    return seed


def get_leech(doc):
    leech = 0
    leech_item= doc.select_one('.leech b')
    if leech_item:
        leech = int(leech_item.text.strip())
    return leech


def get_published(doc):
    published = None
    pi = doc.select_one('p.post-time a')
    if pi:
        published = utils.parse_date(pi.text.strip())
    return published


def get_last_modified(doc):
    lm = None
    lmi = doc.select_one('.posted_since')
    if lmi:
        idx = lmi.text.find('ред. ')
        if idx > 0:
            val = lmi.text[idx+5:idx+20]
            lm = utils.parse_date(val)
    return lm


def get_hash(doc):
    hash = None
    hi = doc.select_one('#tor-hash')
    if hi:
        hash = hi.text.strip()
    return hash


def get_downloads(doc):
    downloads = 0
    for n in doc.select('li'):
        if (n.text.startswith('Скачан')):
            downloads = utils.extract_int(n.text)
    return downloads

def get_user(doc):
    user = 0
    for n in doc.select('a'):
        if (n.text.startswith('[Профиль]')):
            q = urlparse(n.get('href')).query
            ps = parse_qs(q)
            if 'u' in ps:
                user = ps['u'][0]
    return user

gdiff = dict()
gdiff['seed'] = 0
gdiff['leech'] = 0
gdiff['downloads'] = 0
gdiff['sum']=0
gdiff['sqsum'] = 0

def process():
    r = random.randint(-2, 4)
    if r > 0:
        t = source.get_torrent()
        print('get_torrent')
    else:
        t = source.get_check_torrent()
        print('get_check_torrent')
    if t == None:
        return
    print(t['id'], t['title'])

    doc, error = rutracker.get_topic(t['id'])
    if error is not None:
        print(error)
        return
    topic = dict()
    topic['id'] = t['id']
    topic['forum'] = get_forum(doc)
    topic['title'] = t['title']
    topic['title'] = get_title(doc)
    topic['seed'] = get_seed(doc)
    topic['leech'] = get_leech(doc)
    topic['published'] = get_published(doc)
    topic['last_modified'] = get_last_modified(doc)
    topic['hash'] = get_hash(doc)
    topic['downloads'] = get_downloads(doc)
    topic['last_checked'] = datetime.datetime.now()
    topic['user_id'] = get_user(doc)
    print(topic)
    diff = dict()
    diff['seed'] = topic['seed'] - int(t['seed'] or 0)
    diff['leech'] = topic['leech'] - int(t['leech'] or 0)
    diff['downloads'] = topic['downloads'] - int(t['downloads'] or 0)
    if 'expected' in t:
        diff['sum'] = topic['downloads'] - int(t['downloads'] or 0) - int(t['expected'] or 0)
    else:
        diff['sum'] = topic['downloads'] - int(t['downloads'] or 0)
    print(diff)
    gdiff['seed'] = gdiff['seed']  + diff['seed']
    gdiff['leech'] = gdiff['leech'] + diff['leech']
    gdiff['downloads'] = gdiff['downloads'] + diff['downloads']
    gdiff['sum'] = gdiff['sum'] + diff['sum']
    gdiff['sqsum'] = gdiff['sqsum'] + diff['sum']*diff['sum']
    source.update_torrent(topic)
    print('')


items = 1
start = datetime.datetime.now()
source._db.execute('insert into task_checked(start, finish, count, diff, stddev) values(?, ?, ?, ?, ?)', (start, start, 0, 0, 0,))
source._db.commit()
while True:
    if items > 256:
        break
    print('---------------------')
    now = datetime.datetime.now()
    print(items, now, now-start)
    print((256-items)*(now-start)/items)
    print(gdiff)
    if items > 1:
        stddev = math.sqrt((gdiff['sqsum']-gdiff['sum']*gdiff['sum']/items)/(items-1))
        source._db.execute('update task_checked set finish=?, count=?, diff=?, stddev=? where start=?', (datetime.datetime.now(), items, gdiff['sum'], stddev, start,))
        source._db.commit()
    items += 1
    process()
    time.sleep(0 + random.randint(0, 4))

print('')
for item in source._db.execute('''select * from torrents_by_months where p like
"%2018%" or p like "%2017%" or p like "%2016%"'''):
    print(tuple(item))
print('')
for item in source._db.execute('''select * from torrents_by_years where p like 
"%2018%" or p like "%2017%" or p like "%2016%"'''):
    print(tuple(item))

for y in range(2015, 2020):
    print('----', y, '----')
    for item in source._db.execute('''select downloads, title from torrents
where substr(published,1,4)=? order by downloads desc limit 25''', (str(y),)):
        print(tuple(item))
