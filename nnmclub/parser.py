import locale
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nnmclub.models import Forum, Topic

DATETIME_FORMAT = "%d %b %Y %H:%M:%S"


async def get_forums(ref):
    forums = []
    s = requests.Session()
    try:
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("td.leftnav > table.pline")
        for href in tables[1].select("td.row1 a.genmed"):
            forums.append(Forum.parse(href))
        return forums
    except Exception as exc:
        print(exc)
        return None


async def get_topics(forum, start=0):
    topics = []
    s = requests.Session()
    try:
        ref = "http://nnmclub.to/forum/portal.php?c={}".format(forum.id)
        if start > 0:
            ref = "{}&start={}".format(ref, start)
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("table.pline")
        for i, table in enumerate(tables):
            titles = table.select("td.pcatHead h2.substr a.pgenmed")
            if titles:
                topics.append(
                    Topic(id=-1, name=titles[0].get("title"), published=parse_published(table),
                          likes=parse_likes(table)))
        return topics
    except Exception as exc:
        print(exc)
        return None


def parse_published(table):
    published: datetime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    for line in table.select("span.genmed"):
        parts = line.text.split("|")
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        published = datetime.strptime(parts[1].strip(), DATETIME_FORMAT)
        print("\tLINE: {} - {}".format(parts[1], published))
    return published


def parse_likes(table):
    likes = table.select("span.pcomm.bold[id]")
    if likes:
        return int(likes[0].text)
    return 0
