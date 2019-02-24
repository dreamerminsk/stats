import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import rutracker
import utils
import source
import datetime
import time
import random


def get_title(doc):
    title = None
    t = doc.select_one('title')
    if t:
        title = t.text.strip()
    return title


def get_registered(doc):
    registered = None
    for item in doc.select('table.user_details tr'):
        if 'Зарегистрирован' in item.text:
            r = item.select_one('td b')
            if r:
                registered = r.text.strip()
    return registered


def get_nation(doc):
    nation = None
    for item in doc.select('table.user_details tr'):
        if 'Откуда' in item.text:
            r = item.select_one('td img')
            if r:
                nation = r.get('title')
    return nation


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

c = source._db.execute('select distinct user_id from torrents as t left join users as u on t.user_id=u.id where u.id is null limit 320;')
for user in c:
    if user['user_id'] is None:
        continue
    if user['user_id'] < 1:
        continue
    time.sleep(2)
    print(user['user_id'])
    doc, error = rutracker.get_user(user['user_id'])
    if error is not None:
        print(error)
        continue
    name = get_title(doc)
    registered = get_registered(doc)
    nation = get_nation(doc)
    print(name, registered, nation)
    source._db.execute('insert into users values(?, ?, ?, ?)', (user['user_id'], name, registered,nation,))
    source._db.commit()
    q = source._db.execute('select u.name, count(t.id), sum(t.downloads) as user from users as u inner join torrents as t on u.id=t.user_id where u.id=? group by u.name', (user['user_id'],))
    for qi in q:
        print(qi[0], qi[1], qi[2])
    