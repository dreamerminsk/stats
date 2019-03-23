import time

import rutracker
import source
from src import api


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


def parse_user(doc):
    u = {}
    u['id'] = user['user_id']
    u['name'] = get_title(doc)
    u['registered'] = get_registered(doc)
    u['nation'] = get_nation(doc)
    return u


c = source._db.execute('select distinct user_id from torrents as t left join users as u on t.user_id=u.id where u.id '
                       'is null limit 320;')
us = []
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
    u = parse_user(doc)
    u['id'] = user['user_id']
    print(u)
    us.append(u)
    if len(us) == 32:
        b = {}
        b['data'] = us
        r = api.users.create(body=b)
        print(r.status_code)
        print(r.body)
        for usr in us:
            source.insert_user(usr)
        us = []
    q = source._db.execute(
        'select u.name, count(t.id), sum(t.downloads) as user from users as u inner join torrents as t on u.id=t.user_id where u.id=? group by u.name',
        (u['id'],))
    for qi in q:
        print(qi[0], qi[1], qi[2])

if len(us) > 0:
    b = {}
    b['data'] = us
    r = api.users.create(body=b)
    print(r.status_code)
    print(r.body)
    for usr in us:
        source.insert_user(usr)
