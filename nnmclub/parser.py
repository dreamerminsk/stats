import requests
from bs4 import BeautifulSoup

from nnmclub.models import Forum, Topic


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
                    Topic(id=-1, name=titles[0].get("title"), likes=parse_likes(table)))
        return topics
    except Exception as exc:
        print(exc)
        return None


def parse_likes(table):
    likes = table.select("span.pcomm.bold[id]")
    if likes:
        return int(likes[0].text)
    return 0
